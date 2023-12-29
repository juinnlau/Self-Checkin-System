import sqlite3

# Connect to the SQLite database (this will create a new database if it doesn't exist)
conn = sqlite3.connect('qr_database.db')

# Create a cursor object to execute SQL statements
cursor = conn.cursor()

# Create a table named 'admin' with columns 'username' and 'password'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT,
        password TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        name TEXT,
        seat TEXT,
        role TEXT,
        registerdate TEXT,
        checkin1 TEXT,
        checkin2 TEXT,
        checkin3 TEXT
       
    )
''')


# Insert a record into the 'admin' table
#cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('mforce_admin', 'mforce_admin'))
#cursor.execute("DELETE FROM admin WHERE username = 'mforce_admin'")


# Commit the changes and close the connection
conn.commit()
conn.close()
