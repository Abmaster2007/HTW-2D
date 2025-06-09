import sqlite3
from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('Gamemenu.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('Login.html')

@app.route('/login_submit', methods=['GET', 'POST'])
def login_submit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('HTW-2D/database/database.db')
        conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
        cursor = conn.cursor()

        user = cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    
        if user and check_password_hash(user['password'], password):  # Access password using key
            session.clear()
            session['user_id'] = user['id']  # Access user ID using key
            session['username'] = user['username']  # Access username using key
            return redirect(url_for('index'))
        elif user and not check_password_hash(user['password'], password):
            flash('Invalid password. Please try again.', 'danger')
            return redirect(url_for('login'))
        else:
            flash('Username not found. Please try again.', 'danger')
            return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('Signup.html')

@app.route('/signup_submit', methods=['GET', 'POST'])
def signup_submit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['confirmPassword']

        if password != password_confirm:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))
 
        confirm_password = generate_password_hash(password)
        # Check if the username already exists
        conn = sqlite3.connect('HTW-2D/database/database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, confirm_password))
        conn.commit()
        conn.close()
        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/debug_session')
def debug_session():
    if 'user_id' in session:
        conn = sqlite3.connect('HTW-2D/database/database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user = cursor.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
        conn.close()

        if user:
            return f"Session active for user: {session['username']}<br>Database record: {dict(user)}"
        else:
            return "Session active but user not found in database."
    else:
        return "No active session."

if __name__ == '__main__':
    app.run(debug=True)