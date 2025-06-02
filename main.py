import sqlite3
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Gamemenu.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/signup')
def signup():
    return render_template('Signup.html')

if __name__ == '__main__':
    app.run(debug=True)