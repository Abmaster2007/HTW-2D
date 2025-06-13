import sqlite3
from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import random

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]  # 0 = wall, 1 = path

    def generate_maze(self):
        stack = [(1, 1)]  # Start carving from the top-left corner
        self.grid[1][1] = 1  # Mark the starting point as a path

        while stack:
            x, y = stack.pop()
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right
            random.shuffle(directions)  # Randomize directions

            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2  # Move two steps in the chosen direction
                if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] == 0:
                    self.grid[y + dy][x + dx] = 1  # Carve path between current and next cell
                    self.grid[ny][nx] = 1  # Carve path at the next cell
                    stack.append((nx, ny))  # Add the next cell to the stack

    def get_maze(self):
        return self.grid

class Hunter:
    def __init__(self, x, y, ammo=5):
        self.x = x
        self.y = y
        self.ammo = ammo

    def move(self, direction, maze):
        new_x, new_y = self.x, self.y

        if direction == "up" and self.y > 0:
            new_y -= 1
        elif direction == "down" and self.y < len(maze) - 1:
            new_y += 1
        elif direction == "left" and self.x > 0:
            new_x -= 1
        elif direction == "right" and self.x < len(maze[0]) - 1:
            new_x += 1

        # Check if the new position is a path
        if maze[new_y][new_x] == 1:
            self.x, self.y = new_x, new_y

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return True  # Shot fired
        return False  # No ammo left

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
            return render_template('Login.html')
        else:
            flash('Username not found. Please try again.', 'danger')
            return render_template('Login.html')

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
            return render_template('Signup.html')

        confirm_password = generate_password_hash(password)
        # Check if the username already exists
        conn = sqlite3.connect('HTW-2D/database/database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('Signup.html')

        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, confirm_password))
        conn.commit()
        conn.close()
        flash('Signup successful! You can now log in.', 'success')
        return render_template('Login.html')


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

@app.route('/Gameplay')
def gameplay():
    if 'user_id' not in session:
        flash('You must be logged in to access the game.', 'warning')
        return redirect(url_for('login'))
    return render_template('Gameplay.html')

@app.route('/generate_maze', methods=['GET'])
def generate_maze():
    multiplier = int(request.args.get('multiplier', 1))
    base_width, base_height = 21, 11
    width = base_width * multiplier
    height = base_height * multiplier

    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    maze = Maze(width, height)
    maze.generate_maze()

    hunter = Hunter(0, 0)
    valid_position_found = False
    while not valid_position_found:
        random_x = random.randint(0, width - 1)
        random_y = random.randint(0, height - 1)
        if maze.grid[random_y][random_x] == 1:
            hunter.x = random_x
            hunter.y = random_y
            valid_position_found = True

    response = {"maze": maze.get_maze(), "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo}}
    print(response)  # Debugging: Print the response to the console
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)