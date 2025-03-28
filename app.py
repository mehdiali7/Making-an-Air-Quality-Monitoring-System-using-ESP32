from flask import Flask, request, render_template, send_from_directory
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Configuration
DATABASE = 'sensor_data.db'
FIRMWARE_FOLDER = 'firmware'
ALLOWED_EXTENSIONS = {'bin'}
update_available = False

# Ensure directories exist
os.makedirs(FIRMWARE_FOLDER, exist_ok=True)

def init_db():
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
init_db()

# -------------------- OTA Endpoints --------------------
@app.route('/check-update')
def check_update():
    global update_available
    if update_available:
        update_available = False
        return "update_available", 200
    return "no_update", 200

@app.route('/firmware.bin')
def serve_firmware():
    return send_from_directory(FIRMWARE_FOLDER, 'firmware.bin')

@app.route('/upload-firmware', methods=['POST'])
def upload_firmware():
    global update_available
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        file.save(os.path.join(FIRMWARE_FOLDER, 'firmware.bin'))
        update_available = True
        return 'Firmware uploaded successfully', 200
    return 'Invalid file type (only .bin allowed)', 400

# -------------------- Existing Endpoints --------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 10')
            data = cursor.fetchall()
            
        return render_template('index.html', data=data)
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        return "Internal Server Error", 500

@app.route('/data', methods=['GET'])
def save_data():
    temperature = request.args.get('temp')
    humidity = request.args.get('humidity')

    if not temperature or not humidity:
        return "Invalid data", 400

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
