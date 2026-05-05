from flask import Flask, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

# Serve static files from the current directory
app = Flask(__name__, static_folder='.')
CORS(app)
app.secret_key = 'bhardwaj_admin_secure_key_123'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev_default_secret_key')
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'lawyer123')

DB_FILE = 'database.db'

def init_db():
    """Initialize the SQLite database and create the contacts table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            submitted_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Route to serve the main HTML page
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Fallback route to serve CSS, Images, and other static files
@app.route('/<path:path>')
def serve_file(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404

# API Endpoint to handle form submissions
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Extract form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        category = request.form.get('category')
        description = request.form.get('description')
        
        # Insert data into database
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO contacts (name, phone, email, category, description, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, category, description, datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Request saved successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['logged_in'] = True
            return redirect('/admin/leads')
        return "<script>alert('Invalid Admin Username or Password!'); window.location.href='/login';</script>"
    return send_from_directory('.', 'login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/admin/leads')
def admin_leads():
    # Security check: bounce to login if not authenticated
    if not session.get('logged_in'):
        return redirect('/login')
        
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT * FROM contacts ORDER BY submitted_at DESC')
        leads = c.fetchall()
        conn.close()
        
        html = '''
        <div style="font-family: sans-serif; padding: 2rem; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2 style="color: #0F2A4A; margin: 0;">Bhardwaj & Associates - Client Requests</h2>
                <a href="/logout" style="background-color: #8C1515; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-weight: bold;">Logout</a>
            </div>
            <table border="1" cellpadding="12" style="border-collapse: collapse; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <tr style="background-color: #0F2A4A; color: white; text-align: left;">
                    <th>ID</th><th>Client Name</th><th>Mobile</th><th>Email</th><th>Category</th><th>Case Description</th><th>Submission Date</th>
                </tr>
        '''
        if not leads:
            html += '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No requests submitted yet!</td></tr>'
            
        for lead in leads:
            # lead indices correspond to table columns: 0=id, 1=name, 2=phone, 3=email, 4=category, 5=description, 6=submitted_at
            html += f'''
                <tr style="background-color: #ffffff; border-bottom: 1px solid #ddd;">
                    <td>{lead[0]}</td>
                    <td><strong>{lead[1]}</strong></td>
                    <td>{lead[2]}</td>
                    <td><a href="mailto:{lead[3]}">{lead[3]}</a></td>
                    <td><span style="background: #e2e8f0; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;">{lead[4]}</span></td>
                    <td style="max-width: 400px; word-wrap: break-word;">{lead[5]}</td>
                    <td style="color: #666; font-size: 0.9em;">{lead[6][:19]}</td>
                </tr>
            '''
        html += '</table></div>'
        return html
    except Exception as e:
        return f"Error loading database: {str(e)}"

if __name__ == '__main__':
    init_db()
    print("="*60)
    print("Starting Server!")
    print("Access your website at: http://127.0.0.1:5000")
    print("Your form submissions will be saved in 'database.db'.")
    print("="*60)
    app.run(debug=True, port=5000)
