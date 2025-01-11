from flask import Flask, request, jsonify, send_file
import qrcode
import sqlite3
import io
from datetime import datetime

app = Flask(__name__)

# Route to check if the server is running
@app.route('/', methods=['GET'])
def home():
    return "Welcome to Present Sir Backend!"

# Route to initialize the SQLite database
@app.route('/init_db', methods=['GET'])
def init_db():
    try:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                usn TEXT PRIMARY KEY,
                student_name TEXT,
                subject TEXT,
                faculty_name TEXT,
                date TEXT,
                time TEXT
            )
        ''')
        conn.commit()
        return "Database initialized!"
    except Exception as e:
        return f"Error initializing database: {str(e)}"
    finally:
        conn.close()

# Route to generate QR code for attendance
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json
    student_name = data.get("student_name")
    usn = data.get("usn")
    subject = data.get("subject")
    faculty_name = data.get("faculty_name")
    
    # Use current date and time for the QR code content
    current_datetime = datetime.now()
    date = current_datetime.strftime('%Y-%m-%d')
    time = current_datetime.strftime('%H:%M:%S')

    # Create the QR code content
    qr_content = f"Name: {student_name}, USN: {usn}, Date: {date}, Time: {time}, Subject: {subject}, Faculty: {faculty_name}"

    # Generate the QR code
    qr_img = qrcode.make(qr_content)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='qr_code.png')

# Route to save attendance in the database
@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    try:
        # Extract data from the request (assuming JSON input)
        data = request.json
        usn = data.get('usn')
        student_name = data.get('student_name')
        subject = data.get('subject')
        faculty_name = data.get('faculty_name')
        date = data.get('date')
        time = data.get('time')

        # Check if all required fields are present
        if not (usn and student_name and subject and faculty_name and date and time):
            return jsonify({"error": "Missing required fields"}), 400

        # Connect to the database
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()

        # Insert data into the table
        cursor.execute('''
            INSERT INTO attendance (usn, student_name, subject, faculty_name, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usn, student_name, subject, faculty_name, date, time))

        # Commit the transaction
        conn.commit()
        return jsonify({"message": "Attendance record saved successfully!"}), 201

    except sqlite3.IntegrityError as e:
        # Handle duplicate USN error (primary key violation)
        return jsonify({"error": f"Duplicate entry: {str(e)}"}), 400
    except Exception as e:
        # Handle other exceptions
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        conn.close()

# Route to get all attendance records
@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    try:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute('SELECT * FROM attendance')
        rows = c.fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
