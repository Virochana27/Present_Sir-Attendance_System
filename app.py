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

# Faculty page to generate QR codes
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
        session_id = request.form.get('session_id')
        subject = request.form.get('subject')
        faculty_id = request.form.get('faculty_id')
        faculty_name = request.form.get('faculty_name')
        room_number = request.form.get('room_number')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        # Generate timestamp for validation (as seconds since epoch)
        current_time = datetime.now()
        timestamp_number = int(current_time.timestamp())

        # Generate QR code content with 9 fields
        qr_content = (
            f"{session_id}|{subject}|{faculty_id}|{faculty_name}|"
            f"{room_number}|{date}|{start_time}|{end_time}|{timestamp_number}"
        )

        try:
            # Insert session data into the sessions table
            conn = sqlite3.connect('attendance.db', check_same_thread=False, timeout=10)
            c = conn.cursor()
            c.execute('''
                INSERT INTO sessions (session_id, subject, faculty_id, faculty_name, 
                                      room_number, date, start_time, end_time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                (session_id, subject, faculty_id, faculty_name, room_number, 
                 date, start_time, end_time))
            conn.commit()  # Make sure changes are saved to the database
            
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
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                date=date
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
        usn = data.get("usn")
        qr_data = data.get("qr_data")
        device_id = request.remote_addr  # Use IP address as device ID
        current_time = datetime.now()
        date = current_time.strftime('%Y-%m-%d')
        time_str = current_time.strftime('%H:%M:%S')

        try:
            # Parse QR code content (9 fields expected)
            qr_parts = qr_data.split('|')
            if len(qr_parts) != 9:
                message = f"Invalid QR code format. Expected 9 fields."
                message_type = 'error'
                # Store message in session
                session['message'] = message
                session['message_type'] = message_type
                return redirect(url_for('student'))

            # Unpack QR code fields
            session_id, subject, faculty_id, faculty_name, room_number, qr_date, qr_start_time, qr_end_time, qr_timestamp = qr_parts

            # Validate timestamp (QR code time vs current time)
            qr_time = datetime.fromtimestamp(int(qr_timestamp))
            time_difference = abs((current_time - qr_time).total_seconds())
            if time_difference > 1800:  # Allow 30 minutes for validation
                message = "QR code has expired. Please try again."
                message_type = 'error'
                # Store message in session
                session['message'] = message
                session['message_type'] = message_type
                return redirect(url_for('student'))

            # Mark attendance in the database
            conn = sqlite3.connect('attendance.db')
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO attendance (usn, session_id, student_name, device_id, date, time)
                VALUES (?, ?, ?, ?, ?, ?) 
            ''', (usn, session_id, student_name, device_id, date, time_str))
            conn.commit()
            conn.close()

            message = "Attendance marked successfully!"
            message_type = 'success'
            # Store message in session
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

if __name__ == '__main__':
    app.run(debug=True)
