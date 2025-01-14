from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import qrcode
import sqlite3
import io
from datetime import datetime
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set your secret key for sessions

# Home route
@app.route('/')
def home():
    return render_template('home.html')

def get_data_with_parameter_from_db(query, params):
    try:
        conn = sqlite3.connect('college.db')  # Connect to the SQLite database
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()  # Fetch one record
        return result[0] if result else "Unknown"  # Return the value if found, else "Unknown"
    finally:
        conn.close()  # Close the database connection

def get_data_from_db(query):
    try:
        conn = sqlite3.connect('college.db')  # Connect to the SQLite database
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()  # Fetch one record
        return result[0] if result else "Unknown"  # Return the value if found, else "Unknown"
    finally:
         conn.close()  # Close the database connection
# Endpoint to fetch faculty name
@app.route('/get_faculty_name', methods=['POST'])
def get_faculty_name():
    faculty_id = request.json.get('faculty_id')
    if not faculty_id:
        return jsonify({"error": "Faculty ID is required"}), 400
    
    query = "SELECT faculty_name FROM Faculty WHERE faculty_id = ?"
    faculty_name = get_data_with_parameter_from_db(query, (faculty_id.upper(),))
    
    return jsonify({"faculty_name": faculty_name})

# Endpoint to fetch subject name
@app.route('/get_subject_name', methods=['POST'])
def get_subject_name():
    subject_code = request.json.get('subject_code')
    if not subject_code:
        return jsonify({"error": "Subject Code is required"}), 400
    
    query = "SELECT subject_name FROM Subject WHERE subject_code = ?"
    subject_name = get_data_with_parameter_from_db(query, (subject_code,))
    
    return jsonify({"subject_name": subject_name})

@app.route('/get_session_id', methods=['POST'])
def get_session_id():    
    query = "SELECT MAX(session_id) FROM sessions"
    last_session_id = get_data_from_db(query)
    session_id = int(last_session_id) + 1 if last_session_id else 1
    return jsonify({"session_id": session_id})

# Faculty page to generate QR codes
@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
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
            # Connect to the database
            conn = sqlite3.connect('college.db', check_same_thread=False, timeout=10)
            c = conn.cursor()

            # Fetch the last session_id and increment it
            c.execute('SELECT MAX(session_id) FROM sessions')
            last_session_id = c.fetchone()[0]
            session_id = int(last_session_id) + 1 if last_session_id else 1
            # Insert session data into the Sessions table
            c.execute('''
                INSERT INTO sessions (session_id, department, sem, section, faculty_id, subject_code, room, date, start_time, end_time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (session_id, department, sem, section, faculty_id, subject_code, room, date, start_time, end_time))
            conn.commit()
            

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
            conn.close()  # Close the connection after use

            return render_template(
                'faculty.html',
                qr_code=qr_code_base64,
            )

        except sqlite3.IntegrityError as e:
            conn.close()  # Close the connection if unique constraint error occurs
            session['message'] = f"IntegrityError: {e}"  # Store error message in session
            return redirect(url_for('faculty'))  # Redirect to the same page to display the message
        except Exception as e:
            conn.close()  # Ensure connection is closed if any other error occurs
            session['message'] = f"Error generating QR code or inserting data: {e}"  # Store error message in session
            return redirect(url_for('faculty'))  # Redirect to the same page to display the message

    return render_template('faculty.html', message=message)


@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        conn = sqlite3.connect('college.db', check_same_thread=False, timeout=10)
        c = conn.cursor()
        # Fetch the last session_id and increment it
        c.execute('SELECT MAX(session_id) FROM sessions')
        last_session_id = c.fetchone()[0]
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

            # Mark attendance in the database
            conn = sqlite3.connect('college.db')
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO attendance (session_id, usn, student_name) 
                VALUES (?, ?, ?) 
            ''', (session_id, usn, student_name))
            conn.commit()
            conn.close()

            message = "Attendance marked successfully!"
            message_type = 'success'
            session['message'] = message
            session['message_type'] = message_type
            return redirect(url_for('student'))

        except sqlite3.IntegrityError as e:
            conn.close()  # Close the connection if unique constraint error occurs
            message = "Attendance already marked for this session."
            message_type = 'error'
            session['message'] = message
            session['message_type'] = message_type
            return redirect(url_for('student'))
        except Exception as e:
            conn.close()  # Ensure connection is closed if any other error occurs
            message = f"Invalid QR data or other error: {str(e)}"
            message_type = 'error'
            session['message'] = message
            session['message_type'] = message_type
            return redirect(url_for('student'))

    return render_template('student.html', message=message, message_type=message_type)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use PORT from the environment or default to 5000
    app.run(host="0.0.0.0", port=port)  #app.run(debug=True)
