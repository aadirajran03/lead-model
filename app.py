from flask import Flask, render_template, request, redirect, url_for, flash
from lead_scoring import LeadScoring
from fb_sync import get_facebook_leads
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_PATH = 'leads.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            experience INTEGER,
            location TEXT,
            category TEXT,
            score INTEGER
        )''')

def auto_sync_fb_leads():
    print("⏳ Auto-syncing leads from Facebook...")
    ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
    PAGE_ID = 'YOUR_PAGE_ID'
    FORM_ID = 'YOUR_FORM_ID'

    leads = get_facebook_leads(ACCESS_TOKEN, PAGE_ID, FORM_ID)
    for lead in leads:
        fields = {f['name']: f['values'][0] for f in lead.get('field_data', [])}
        name = fields.get('full_name', 'Unknown')
        email = fields.get('email', '')
        phone = fields.get('phone_number', '')
        experience = 3
        location = 'Delhi'
        score, category = LeadScoring.score(experience, location)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM leads WHERE email = ?", (email,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO leads (name, email, phone, experience, location, category, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (name, email, phone, experience, location, category, score))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, COUNT(*) FROM leads GROUP BY category")
        data = cursor.fetchall()
    categories = [d[0] for d in data]
    counts = [d[1] for d in data]
    return render_template("dashboard.html", categories=categories, counts=counts)

@app.route('/add', methods=['GET', 'POST'])
def add_manual():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        experience = int(request.form['experience'])
        location = request.form['location']
        score, category = LeadScoring.score(experience, location)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO leads (name, email, phone, experience, location, category, score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (name, email, phone, experience, location, category, score))
        flash('Lead added successfully!', 'success')
        return redirect(url_for('view_leads'))
    return render_template("manual_lead.html")

@app.route('/leads')
def view_leads():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads")
        leads = cursor.fetchall()
    return render_template("view_leads.html", leads=leads)

@app.route('/sync_fb_leads')
def sync_fb_leads():
    auto_sync_fb_leads()
    flash('Facebook leads synced manually.', 'success')
    return redirect(url_for('view_leads'))

if __name__ == '__main__':
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=auto_sync_fb_leads, trigger="interval", minutes=5)
    scheduler.start()
    try:
        app.run(debug=True)
    except:
        scheduler.shutdown()
