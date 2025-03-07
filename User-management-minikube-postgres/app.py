from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from pydantic import BaseModel, Field

# Pydantic model for data validation
class User(BaseModel):
    name: str
    id: str
    age: int
    gender: str

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'postgres'),
        database=os.environ.get('DB_NAME', 'userdb'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres')
    )
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/post_data', methods=['GET', 'POST'])
def post_data():
    if request.method == 'POST':
        try:
            user_data = User(
                name=request.form['name'],
                id=request.form['id'],
                age=int(request.form['age']),
                gender=request.form['gender']
            )
            
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO users (name, id, age, gender) VALUES (%s, %s, %s, %s)',
                (user_data.name, user_data.id, user_data.age, user_data.gender)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            return redirect(url_for('see_data'))
        except Exception as e:
            return f"Error: {str(e)}", 400
    
    return render_template('post_data.html')

@app.route('/see_data')
def see_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users;')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('see_data.html', users=users)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            name VARCHAR(100) NOT NULL,
            id VARCHAR(50) PRIMARY KEY,
            age INTEGER NOT NULL,
            gender VARCHAR(10) NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)