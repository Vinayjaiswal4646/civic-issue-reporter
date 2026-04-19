from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🧱 Create database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            image TEXT,
            latitude TEXT,
            longitude TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()
# 🏠 Home page
# 🏠 Home page
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM issues")
    issues = c.fetchall()

    conn.close()

    print("DB DATA:", issues)  # debug

    return render_template('index.html', issues=issues)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    
    if request.method == 'POST':
        title = request.form['title']
        file = request.files['image']

        # ✅ MOVE HERE
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            c.execute(
                "INSERT INTO issues (title, image, latitude, longitude) VALUES (?, ?, ?, ?)",
                (title, filepath, latitude, longitude)
            )

            conn.commit()
            conn.close()

            print("FORM DATA:", request.form)

        return redirect(url_for('index'))

    return render_template('upload.html')

# ▶️ Run app
if __name__ == '__main__':

    app.run(debug=True)