from flask import Flask, request, render_template
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'sensor_data.db'

def init_db():
    # Create database and table if not exists
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL
            )
        ''')
        conn.commit()

# Initialize database
init_db()

@app.route('/')
def home():
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row  # For dictionary-like access
            cursor = conn.cursor()
            
            # Get last 10 entries ordered by timestamp
            cursor.execute('''
                SELECT * FROM readings
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            data = cursor.fetchall()
            
        return render_template('index.html', data=data)
    
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        return "Internal Server Error", 500

@app.route('/data', methods=['GET'])
def save_data():
    # Get temperature and humidity from the request
    temperature = request.args.get('temp')
    humidity = request.args.get('humidity')

    # Validate the data
    if not temperature or not humidity:
        return "Invalid data", 400

    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO readings (timestamp, temperature, humidity)
                VALUES (?, ?, ?)
            ''', (timestamp, temperature, humidity))
            conn.commit()

        print(f"[{timestamp}] Data Received: Temperature = {temperature}C, Humidity = {humidity}%")
        return "Data Received!", 200
    
    except Exception as e:
        print(f"Error saving data: {str(e)}")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
