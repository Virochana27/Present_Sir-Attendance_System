from flask import Flask, render_template, request, jsonify, redirect, url_for
import qrcode
import sqlite3
import io
from datetime import datetime
import base64

app = Flask(__name__)

# Initialize the SQLite database
@app.route('/init_db', methods=['GET'])
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            subject TEXT,
            faculty_id TEXT,
            faculty_name TEXT,
            room_number TEXT,
            date TEXT,
            start_time TEXT,
            end_time TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            usn TEXT,
            session_id TEXT,
            student_name TEXT,
            device_id TEXT,
            date TEXT,
            time TEXT,
            PRIMARY KEY (usn, session_id)
        )
    ''')
    conn.commit()
    conn.close()
    return "Database initialized!"

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Faculty page to generate QR codes
@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
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
            conn.close()

            # Generate the QR code
            qr_img = qrcode.make(qr_content)

            # Save the QR code to a binary stream
            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            buffer.seek(0)

            # Encode the QR code image as a base64 string
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return render_template(
                'faculty.html',
                qr_code=qr_code_base64,
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                date=date
            )

        except Exception as e:
            print(f"Error generating QR code or inserting data: {e}")
            return "Failed to generate QR code or insert data into the database.", 500

    return render_template('faculty.html', qr_code=None)


# Student page to scan QR code and mark attendance
@app.route('/student', methods=['GET', 'POST'])
def student():
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
                return jsonify({"error": f"Invalid QR code format. Expected 9 fields, got {len(qr_parts)}."}), 400

            # Unpack QR code fields
            session_id, subject, faculty_id, faculty_name, room_number, qr_date, qr_start_time, qr_end_time, qr_timestamp = qr_parts

            # Validate timestamp (QR code time vs current time)
            qr_time = datetime.fromtimestamp(int(qr_timestamp))
            time_difference = abs((current_time - qr_time).total_seconds())
            if time_difference > 1800:  # Allow 30 minutes for validation
                return jsonify({"error": "QR code has expired. Please try again."}), 400

            # Mark attendance in the database
            conn = sqlite3.connect('attendance.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO attendance (usn, session_id, student_name, device_id, date, time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (usn, session_id, student_name, device_id, date, time_str))
            conn.commit()
            conn.close()

            return jsonify({"message": "Attendance marked successfully!"}), 200

        except Exception as e:
            print(f"Error: {e}")  # Debugging log
            return jsonify({"error": f"Invalid QR data or other error: {str(e)}"}), 400

    return render_template('student.html')

if __name__ == '__main__':
    app.run(debug=True)