from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session
from datetime import datetime, timedelta
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'd7a8f9b3e4c5a6b7c8d9e0f1a2b3c4d5'
app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(days=30) if os.environ.get('REMEMBER_ME') else timedelta(minutes=30),
    SESSION_REFRESH_EACH_REQUEST=True)

# Configuration
DATABASE = 'sensor_data.db'
FIRMWARE_FOLDER = 'firmware'
ALLOWED_EXTENSIONS = {'bin'}
class OTAState:
    update_available = False
    last_update = None
PASSWORD_HASH = generate_password_hash('admin123')

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
init_db()

# -------------------- OTA Endpoints --------------------
@app.route('/check-update')
def check_update():
    if OTAState.update_available:
        OTAState.update_available = False  # Reset after checking
        return "update_available", 200
    return "no_update", 200

@app.route('/firmware.bin')
def serve_firmware():
    return send_from_directory(FIRMWARE_FOLDER, 'firmware.bin')


@app.route('/upload-firmware', methods=['POST'])
def upload_firmware():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
        
    if file and allowed_file(file.filename):
        try:
            filepath = os.path.join(FIRMWARE_FOLDER, 'firmware.bin')
            print(f"Saving to: {filepath}")  # Debug
            
            # Save original file size for verification
            original_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            
            file.save(filepath)
            
            
            OTAState.update_available = True
            OTAState.last_update = datetime.now()
            print(f"Update marked as available at {OTAState.last_update}")
            return '', 200
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return f'Upload failed: {str(e)}', 500
            
    return 'Invalid file type (only .bin allowed)', 400

@app.route('/update-status')
def update_status():
    return {
        'update_available': OTAState.update_available,
        'last_update': OTAState.last_update.isoformat() if OTAState.last_update else None,
        'firmware_size': os.path.getsize(os.path.join(FIRMWARE_FOLDER, 'firmware.bin')) 
            if os.path.exists(os.path.join(FIRMWARE_FOLDER, 'firmware.bin')) else 0
              }

# --------------------login Endpoints --------------------
@app.route('/')
def index():
    # If user is already logged in, redirect to home
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    remember = request.form.get('remember') == 'on'  # Check if checkbox was checked
    
    if password and check_password_hash(PASSWORD_HASH, password):
        session['logged_in'] = True
        session.permanent = remember  # Only make session permanent if "remember me" is checked
        
        if remember:
            # Set longer session lifetime for "remember me"
            app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
        else:
            # Normal session timeout
            app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
            
        return redirect(url_for('home'))
    else:
        return render_template('index.html', error="Invalid password"), 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# -------------------- Remaining Endpoints --------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/home')
def home():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 10')
            data = cursor.fetchall()
            
        return render_template('homepage.html', data=data)
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
    
# -------------------- Navbar page Routes --------------------
@app.route('/firmware')
def firmware():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    return render_template('firmware.html')

@app.route('/aboutus')
def aboutus():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    return render_template('aboutus.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
