import sqlite3

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Create the attendance table if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            usn TEXT PRIMARY KEY,  -- Use USN as primary key
            student_name TEXT,
            subject TEXT,
            faculty_name TEXT,
            date TEXT,
            time TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Call the function to initialize the database
init_db()
