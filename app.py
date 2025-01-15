import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import qrcode
import io
from datetime import datetime
import base64
import sqlite3
from supabase import create_client, Client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set your secret key for sessions

url = os.getenv('URL')
key = os.getenv('KEY')
supabase: Client = create_client(url, key)


# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Endpoint to fetch subject name
@app.route('/get_subject_name', methods=['POST'])
def get_subject_name():
    subject_code = request.json.get('subject_code')
    if not subject_code:
        return jsonify({"error": "Subject Code is required"}), 400
    else:
        try:
        # Execute the query using Supabase
            result = supabase.table('subject').select('subject_name').eq('subject_code', subject_code.upper()).execute()
        # Return the faculty name if found, else "Unknown"
            subject_name=result.data[0]['subject_name'] if result.data else "Unknown"
            return jsonify({"subject_name": subject_name})
        except Exception as e:
            print(f"Error: {e}")
            return "Unknown"

@app.route('/get_session_id', methods=['POST'])
def get_session_id():    
    response = supabase.table('sessions').select('session_id').order('session_id', desc=True).limit(1).execute()

    if response.data:
        last_session_id = response.data[0]['session_id']
        session_id = int(last_session_id) + 1  # Increment session_id
    else:
        session_id = 1  # If no data is found, start from session_id = 1

    if 'faculty_id' in session:
        faculty_id = session['faculty_id']
        try:
    # Execute the query using Supabase
            result = supabase.table('faculty').select('faculty_name').eq('faculty_id', faculty_id.upper()).execute()
        # Return the faculty name if found, else "Unknown"
            faculty_name=result.data[0]['faculty_name'] if result.data else "Unknown"
        except Exception as e:
            print(f"Error: {e}")
            return "Unknown"

    return jsonify({"session_id": session_id, "faculty_id": faculty_id, "faculty_name": faculty_name})

# Faculty page to generate QR codes
@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
    if 'faculty_id' not in session:  # Check if the user is logged in
        return redirect(url_for('login'))  # Redirect to login if not logged in

    faculty_id = session['faculty_id']  # Retrieve the logged-in faculty ID
    message = None  # Initialize message variable

    # Retrieve the message from the session if it exists
    if 'message' in session:
        message = session['message']
        session.pop('message', None)  # Remove the message after displaying it

    if request.method == 'POST':
        # Retrieve form data
        department = request.form.get('department').upper()
        sem = request.form.get('sem')
        section = request.form.get('section').upper()
        faculty_id = request.form.get('faculty_id').upper()
        subject_code = request.form.get('subject_code').upper()
        room = request.form.get('room')
        date = datetime.now().strftime('%Y-%m-%d')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        try:
            # Fetch the last session_id from the sessions table
            result = supabase.table('sessions').select('session_id').order('session_id', desc=True).limit(1).execute()

            last_session_id = result.data[0]['session_id'] if result.data else 0
            session_id = last_session_id + 1
        
        # Insert session data into the sessions table
            data = {
                'session_id': session_id,
                'department': department,
                'sem': sem,
                'section': section,
                'faculty_id': faculty_id,
                'subject_code': subject_code,
                'room': room,
                'date': date,
                'start_time': start_time,
                'end_time': end_time
            }
        
            # Insert the data into the 'sessions' table
            supabase.table('sessions').insert([data]).execute()
        
            # Generate timestamp for validation (as seconds since epoch)
            current_time = datetime.now()
            timestamp_number = int(current_time.timestamp())
            # Generate QR code content with session_id and timestamp
            qr_content = f"{session_id}|{timestamp_number}"
            # Generate the QR code
            qr_img = qrcode.make(qr_content)

            # Save the QR code to a binary stream
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            buffer.seek(0)

            # Encode the QR code image as a base64 string
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            #upload_to_supabase('college.db', 'Present Sir')

            return render_template(
                'faculty.html',
                qr_code=qr_code_base64,
            )

        except Exception as e:
            session['message'] = f"Error: {e}"  # Handle errors
            return redirect(url_for('faculty'))  # Redirect to handle the error

    return render_template('faculty.html', message=message)


@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        result = supabase.table('sessions').select('session_id').order('session_id', desc=True).limit(1).execute()
        last_session_id = result.data[0]['session_id'] if result.data else 1
        session_id = int(last_session_id) if last_session_id else 1
        # Retrieve form data from the request
        # Generate a new timestamp
        current_time = datetime.now()
        timestamp_number = int(current_time.timestamp())

        # Generate new QR code content
        qr_content = (
            f"{session_id}|{timestamp_number}"
        )

        # Create the QR code
        qr_img = qrcode.make(qr_content)
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return jsonify({'qr_code': qr_code_base64, 'timestamp': timestamp_number})
    except Exception as e:
        return jsonify({'error': str(e)})


# Student page to scan QR code and mark attendance
@app.route('/student', methods=['GET', 'POST'])
def student():
    message = None  # Variable to hold success or error message
    message_type = None  # To distinguish between success and error messages

    # Retrieve the message from the session if it exists
    if 'message' in session:
        message = session['message']
        message_type = session['message_type']
        session.pop('message', None)  # Remove the message from the session after displaying

    if request.method == 'POST':
        data = request.form
        student_name = data.get("student_name")
        usn = data.get("usn").upper()
        qr_data = data.get("qr_data")
        current_time = datetime.now()

        try:
            # Parse QR code content (2 fields expected: session_id, timestamp)
            qr_parts = qr_data.split('|')
            if len(qr_parts) != 2:
                message = f"Invalid QR code format."
                message_type = 'error'
                session['message'] = message
                session['message_type'] = message_type
                return redirect(url_for('student'))

            # Unpack QR code fields
            session_id, qr_timestamp = qr_parts

            # Validate timestamp (QR code time vs current time)
            qr_time = datetime.fromtimestamp(int(qr_timestamp))
            time_difference = abs((current_time - qr_time).total_seconds())
            if time_difference > 30:  # Allow 30 seconds for validation
                message = "QR code has expired. Please try again."
                message_type = 'error'
                session['message'] = message
                session['message_type'] = message_type
                return redirect(url_for('student'))

            attendance_data = {
                "session_id": session_id,
                "usn": usn,
                "student_name": student_name
            }
            supabase.table('attendance').insert([attendance_data]).execute()
            message = f"Attendance Marked Successfully!"
            message_type = 'success'
            session['message'] = message
            session['message_type'] = message_type
            return redirect(url_for('student'))
        except Exception as e:
            print(str(e))
            if 'code' in str(e):
                error_code = str(e).split("code': ")[1].split(",")[0]
                print(error_code)
            if error_code=='23505':
                message = "Attendance already marked for this session."
                message_type = 'error'
                session['message'] = message
                session['message_type'] = message_type
                return redirect(url_for('student'))
            else:
                message = f"Error: {str(e)}"
                message_type = 'error'
                session['message'] = message
                session['message_type'] = message_type
                return redirect(url_for('student'))

    return render_template('student.html', message=message, message_type=message_type)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id').upper()
        password = request.form.get('password')

        try:
            # Fetch faculty details from the database
            result = supabase.table('faculty_credentials').select('password').eq('faculty_id', faculty_id).execute()
            if result.data:
                stored_password = result.data[0]['password']
                # Verify the password
                if check_password_hash(stored_password, password):
                    session['faculty_id'] = faculty_id  # Set the faculty ID in the session
                    return redirect(url_for('faculty'))  # Redirect to the faculty page
                else:
                    message = "Invalid password. Please try again."
            else:
                message = "Faculty ID not found."
        except Exception as e:
            message = f"Error: {e}"

    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('faculty_id', None)  # Remove faculty_id from the session
    return redirect(url_for('home'))  # Redirect to the login page


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use PORT from the environment or default to 5000
    app.run(host="0.0.0.0", port=port) 
    #app.run(debug=True)
