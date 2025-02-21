import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

cursor.execute("SELECT * from Students")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.commit()  # Save changes
conn.close()




