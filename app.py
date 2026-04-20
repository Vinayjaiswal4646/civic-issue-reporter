from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🧱 Create database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # ✅ issues table (with status + votes)
    c.execute('''
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        image TEXT,
        latitude TEXT,
        longitude TEXT,
        status TEXT,
        votes INTEGER DEFAULT 0
    )
    ''')

    # ✅ users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    ''')

    # ✅ create admin only once
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin")
        )

    conn.commit()
    conn.close()


init_db()


# 🏠 Home page
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # 🔥 sort by votes
    c.execute("SELECT * FROM issues ORDER BY votes DESC")
    issues = c.fetchall()

    conn.close()

    return render_template('index.html', issues=issues)


# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]
            session['role'] = user[3]

            if user[3] == "admin":
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            return "Invalid login"

    return render_template('login.html')


# 🚪 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# 📤 Upload
@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        file = request.files['image']

        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            c.execute(
                "INSERT INTO issues (title, image, latitude, longitude, status) VALUES (?, ?, ?, ?, ?)",
                (title, filepath, latitude, longitude, "Pending")
            )

            conn.commit()
            conn.close()

        return redirect(url_for('index'))

    return render_template('upload.html')


# 👨‍💼 Admin panel
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return "Access denied"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM issues")
    issues = c.fetchall()

    conn.close()

    return render_template('admin.html', issues=issues)


# 🔄 Update status
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):
    if session.get('role') != 'admin':
        return "Not allowed"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("UPDATE issues SET status=? WHERE id=?", (status, id))

    conn.commit()
    conn.close()

    return redirect('/admin')


# 👍 Upvote
@app.route('/upvote/<int:id>')
def upvote(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("UPDATE issues SET votes = votes + 1 WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/')


# ▶️ Run app
if __name__ == '__main__':
    app.run(debug=True)