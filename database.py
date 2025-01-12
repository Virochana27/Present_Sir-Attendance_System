import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('attendance.db')

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Execute a query to fetch data from the table
cursor.execute("SELECT * FROM sessions")

# Fetch all the rows from the query result
rows = cursor.fetchall()
# Print the fetched data
for row in rows:
    print(row)



# Close the connection
connection.close()
