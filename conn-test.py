import mysql.connector

conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='qui234',
    database='bills'  # This selects the 'bills' DB
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM payments")

for row in cursor.fetchall():
    print(row)

conn.close()
