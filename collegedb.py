"""import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('college.db')
cursor = conn.cursor()

# Create Faculty Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Faculty (
    faculty_id TEXT PRIMARY KEY,
    faculty_name TEXT NOT NULL,
    department TEXT NOT NULL,
    position TEXT NOT NULL,
    date_of_appointment TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL 
);
''')

# Create Subject Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Subject (
    subject_code TEXT PRIMARY KEY,
    subject_name TEXT NOT NULL,
    department TEXT NOT NULL,
    sem INTEGER NOT NULL
);
''')

# Create Sessions Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department TEXT NOT NULL,
    sem INTEGER NOT NULL,
    section TEXT NOT NULL,
    faculty_id TEXT NOT NULL,
    subject_code TEXT NOT NULL,
    room TEXT NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id),
    FOREIGN KEY (subject_code) REFERENCES Subject(subject_code)
);
''')

# Create Attendance Table with Composite Primary Key
cursor.execute('''
CREATE TABLE IF NOT EXISTS Attendance (
    session_id INTEGER NOT NULL,
    usn TEXT NOT NULL,
    student_name TEXT NOT NULL,
    PRIMARY KEY (session_id, usn),  -- Composite primary key
    FOREIGN KEY (usn) REFERENCES Student(usn),
    FOREIGN KEY (session_id) REFERENCES Sessions(session_id)
);
''')


# Create Student Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Student (
    usn TEXT PRIMARY KEY,
    student_name TEXT NOT NULL,
    department TEXT NOT NULL,
    batch TEXT NOT NULL,
    cgpa REAL NOT NULL,
    date_of_birth TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Tables initialized successfully in college.db")
"""

import sqlite3

# Connect to the database
conn = sqlite3.connect('college.db')
cursor = conn.cursor()

# Function to insert Faculty data
def insert_faculty(faculty_id, faculty_name, department, position, date_of_appointment, date_of_birth, email, phone_number):
    cursor.execute('''
    INSERT INTO Faculty (faculty_id, faculty_name, department, position, date_of_appointment, date_of_birth, email, phone_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (faculty_id, faculty_name, department, position, date_of_appointment, date_of_birth, email, phone_number))
    conn.commit()

# Function to insert Subject data
def insert_subject(subject_code, subject_name, department, sem):
    cursor.execute('''
    INSERT INTO Subject (subject_code, subject_name, department, sem)
    VALUES (?, ?, ?, ?)
    ''', (subject_code, subject_name, department, sem))
    conn.commit()

# Function to insert Sessions data
def insert_sessions(department, sem, section, faculty_id, subject_code, room, date, start_time, end_time):
    cursor.execute('''
    INSERT INTO Sessions (department, sem, section, faculty_id, subject_code, room, date, start_time, end_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (department, sem, section, faculty_id, subject_code, room, date, start_time, end_time))
    conn.commit()

# Function to insert Attendance data
def insert_attendance(session_id, usn, student_name):
    cursor.execute('''
    INSERT INTO Attendance (session_id, usn, student_name)
    VALUES (?, ?, ?)
    ''', (session_id, usn, student_name))
    conn.commit()

# Function to insert Student data
def insert_student(usn, student_name, department, batch, cgpa, date_of_birth, phone_number, email):
    cursor.execute('''
    INSERT INTO Student (usn, student_name, department, batch, cgpa, date_of_birth, phone_number, email)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (usn, student_name, department, batch, cgpa, date_of_birth, phone_number, email))
    conn.commit()

"""

import sqlite3

# Connect to the database
conn = sqlite3.connect('college.db')
cursor = conn.cursor()

# Function to update faculty phone number
def update_faculty_phone_number(faculty_id, new_phone_number):
    # Prepare the SQL query to update the faculty phone number
    cursor.execute('''UPDATE Faculty
                      SET email = ?
                      WHERE faculty_id = ?''', (new_phone_number, faculty_id))
    
    # Commit the changes
    conn.commit()
    print("Phone number updated successfully!")

# Example usage: Update phone number for faculty_id 'F001'
update_faculty_phone_number('CS003', 'CS003@university.com')

# Close the connection
conn.close()
"""

# Sample Data Insertions

# Insert Faculty
#insert_faculty("CS003", "Ms. Veeda", "CSE", "Assistant Professor", "2024-09-01", "1999-01-01", "01SUCS003@suiet.com", "9876543214")

# Insert Subject
#insert_subject("22SAL651", "Data Warehouse and Data Mining", "AIML", 6)

# Insert Session
#insert_sessions("AIML", 6, "A", "CS001", "22SAL062", "203", "2025-01-13", "09:00", "09:55")

# Insert Student
#insert_student("AI082", "Yashwith", "AIML", "2022", 9.0, "2001-01-01", "8876543211", "AI082@university.com")

# Insert Attendance
insert_attendance(1, "AI082", "Yashwith")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data inserted successfully into college.db")
