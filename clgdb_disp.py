import sqlite3

# Connect to the database
conn = sqlite3.connect('college.db')
cursor = conn.cursor()

# Function to fetch and display data from Faculty Table
def fetch_faculty_data():
    cursor.execute("SELECT * FROM Faculty")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Function to fetch and display data from Subject Table
def fetch_subject_data():
    cursor.execute("SELECT * FROM Subject")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Function to fetch and display data from Sessions Table
def fetch_sessions_data():
    cursor.execute("SELECT * FROM Sessions")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Function to fetch and display data from Attendance Table
def fetch_attendance_data():
    cursor.execute("SELECT * FROM Attendance")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Function to fetch and display data from Student Table
def fetch_student_data():
    cursor.execute("SELECT * FROM Student")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Call the functions to fetch data from the tables
print("Faculty Data:")
fetch_faculty_data()

print("\nSubject Data:")
fetch_subject_data()

print("\nSessions Data:")
fetch_sessions_data()

print("\nAttendance Data:")
fetch_attendance_data()

print("\nStudent Data:")
fetch_student_data()

# Close the connection
conn.close()
