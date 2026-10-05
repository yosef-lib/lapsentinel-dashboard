from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'lapsentinel.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS devices
                     (hostname TEXT PRIMARY KEY, tenant_id TEXT, 
                      active_nim TEXT, status TEXT, 
                      uptime_minutes INTEGER, last_ping TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS sessions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      hostname TEXT, active_nim TEXT, 
                      timestamp TIMESTAMP)''')

@app.route('/')
def dashboard():
    with get_db() as conn:
        devices = conn.execute('SELECT * FROM devices ORDER BY last_ping DESC').fetchall()
        
        # Hitung statistik
        total_devices = len(devices)
        online_devices = sum(1 for d in devices if d['status'] == 'online')
        active_users = sum(1 for d in devices if d['active_nim'] and d['active_nim'] != 'Unknown')

    return render_template('dashboard.html', devices=devices, total=total_devices, online=online_devices, active=active_users)

@app.route('/api/v1/telemetry', methods=['POST'])
def telemetry():
    data = request.json
    if not data or 'hostname' not in data:
        return jsonify({"error": "Invalid payload"}), 400

    hostname = data['hostname']
    tenant_id = data.get('tenant_id', 'Unknown')
    active_nim = data.get('active_nim', 'Unknown')
    status = data.get('status', 'online')
    uptime = data.get('session_uptime_minutes', 0)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        # Update or Insert Device Status
        conn.execute('''INSERT INTO devices (hostname, tenant_id, active_nim, status, uptime_minutes, last_ping)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(hostname) DO UPDATE SET
                        tenant_id=excluded.tenant_id,
                        active_nim=excluded.active_nim,
                        status=excluded.status,
                        uptime_minutes=excluded.uptime_minutes,
                        last_ping=excluded.last_ping''', 
                     (hostname, tenant_id, active_nim, status, uptime, now))
        
        # Log session if NIM exists
        if active_nim != 'Unknown':
            conn.execute('INSERT INTO sessions (hostname, active_nim, timestamp) VALUES (?, ?, ?)', 
                         (hostname, active_nim, now))

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
