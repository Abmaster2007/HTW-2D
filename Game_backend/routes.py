"""
routes.py

Defines the Flask routes for the Hunt the Wumpus web application, including game initialization, player actions, and leaderboard.
"""

import sqlite3
import random
from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Maze, Hunter, Wumpus, SuperBat, BottomlessPit

def create_routes(app):
    """
    Registers all routes to the Flask app.
    """

    @app.route('/')
    def index():
        """
        Renders the game menu and leaderboard.
        """
        conn = sqlite3.connect('HTW-2D/database/database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT username, time, difficulty FROM leaderboard ORDER BY time ASC")
        rows = cursor.fetchall()
        conn.close()
        return render_template('Gamemenu.html', leaderboard=rows)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        Renders the login page.
        """
        return render_template('Login.html')

    @app.route('/login_submit', methods=['GET', 'POST'])
    def login_submit():
        """
        Handles the login form submission.
        """
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
        """
        Renders the signup page.
        """
        return render_template('Signup.html')

    @app.route('/signup_submit', methods=['GET', 'POST'])
    def signup_submit():
        """
        Handles the signup form submission.
        """
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
        """
        Logs out the current user and redirects to the index page.
        """
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/debug_session')
    def debug_session():
        """
        Displays the current session information for debugging.
        """
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

    @app.route('/generate_maze', methods=['GET'])
    def generate_maze():
        """
        Generates a new maze based on the selected difficulty multiplier.
        """
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

    @app.route('/initialize', methods=['GET'])
    def initialize_game():
        """
        Initializes the game state, placing the hunter, Wumpus, bats, and pits in the maze.
        """
        global maze, hunter, wumpus, superbats, pits

        # Use session values or defaults
        hunter_ammo = session.get('hunter_ammo')
        vision_radius = session.get('vision_radius')
        wumpus_speed = session.get('wumpus_speed')
        wumpus_aggressive = session.get('wumpus_aggressive')
        multiplier = session.get('multiplier')

        width = 21 * multiplier
        height = 11 * multiplier

        # Ensure odd dimensions for maze generation
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1

        maze_obj = Maze(width, height)
        maze_obj.generate_maze()
        maze = maze_obj.get_maze()

        # Place hunter in a valid position
        valid_cells = [(x, y) for y in range(height) for x in range(width) if maze[y][x] == 1]
        hunter_x, hunter_y = random.choice(valid_cells)
        hunter = Hunter(hunter_x, hunter_y, ammo=hunter_ammo)

        # Place Wumpus in a valid position, not on the hunter
        wumpus_cells = [(x, y) for (x, y) in valid_cells if (x, y) != (hunter.x, hunter.y)]
        wumpus_x, wumpus_y = random.choice(wumpus_cells)
        wumpus = Wumpus(wumpus_x, wumpus_y, asleep=True)

        # Place bats and pits
        valid_cells = [(x, y) for y in range(height) for x in range(width) if maze[y][x] == 1 and (x, y) != (hunter.x, hunter.y) and (x, y) != (wumpus.x, wumpus.y)]
        num_bats = session.get('num_bats', 2)
        num_pits = session.get('num_pits', 2)
        bat_positions = random.sample(valid_cells, min(num_bats, len(valid_cells)))
        pit_positions = random.sample([cell for cell in valid_cells if cell not in bat_positions], min(num_pits, len(valid_cells) - len(bat_positions)))
        superbats = [SuperBat(x, y) for (x, y) in bat_positions]
        pits = [BottomlessPit(x, y) for (x, y) in pit_positions]
        response = {
            "maze": maze,
            "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo},
            "wumpus": {"x": wumpus.x, "y": wumpus.y, "asleep": wumpus.asleep, "alive": wumpus.alive},
            "bats": [{"x": bat.x, "y": bat.y} for bat in superbats],
            "pits": [{"x": pit.x, "y": pit.y} for pit in pits],
            "vision_radius": vision_radius,
            "wumpus_speed": wumpus_speed,
            "wumpus_aggressive": wumpus_aggressive,
            "multiplier": multiplier
        }
        return jsonify(response)

    @app.route('/move_hunter', methods=['POST'])
    def move_hunter():
        """
        Moves the hunter in the specified direction and checks for collisions with Wumpus, bats, and pits.
        """
        direction = request.json.get('direction')
        hunter.move(direction, maze)
        # Check for bottomless pit
        for pit in pits:
            if pit.check_fall(hunter):
                hunter_dead = True
                return jsonify({
                    "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo, "dead": True, "fell": True},
                    "wumpus": {"x": wumpus.x, "y": wumpus.y, "asleep": wumpus.asleep, "alive": wumpus.alive}
                })
        # Check for superbat
        for bat in superbats:
            if hunter.x == bat.x and hunter.y == bat.y:
                bat.transport(hunter, maze)
                break  # Only transport once per move

        hunter_dead = (hunter.x == wumpus.x and hunter.y == wumpus.y and wumpus.alive)
        return jsonify({
            "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo, "dead": hunter_dead},
            "wumpus": {"x": wumpus.x, "y": wumpus.y, "asleep": wumpus.asleep, "alive": wumpus.alive},
            "bats": [{"x": bat.x, "y": bat.y} for bat in superbats],
            "pits": [{"x": pit.x, "y": pit.y} for pit in pits]
        })

    @app.route('/shoot', methods=['POST'])
    def shoot():
        """
        Shoots an arrow in the specified direction. If the arrow hits the Wumpus, it will be killed.
        """
        direction = request.json.get('direction')  # Get shooting direction from the client
        result = hunter.shoot(direction, maze, wumpus)
        # wake up the Wumpus if it was asleep
        if wumpus.asleep:
            wumpus.asleep = False
        hunter_dead = (hunter.x == wumpus.x and hunter.y == wumpus.y and wumpus.alive)
        return jsonify({
            "result": result,
            "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo, "dead": hunter_dead},
            "wumpus": {"x": wumpus.x, "y": wumpus.y, "asleep": wumpus.asleep, "alive": wumpus.alive}
        })

    @app.route('/move_wumpus', methods=['POST'])
    def move_wumpus():
        """
        Moves the Wumpus towards the hunter if awake and alive. Can be moved by bats.
        """
        if not wumpus.asleep and wumpus.alive:
            wumpus.move(hunter, maze)
            # Check for superbat (wumpus can be moved by bats)
            for bat in superbats:
                if wumpus.x == bat.x and wumpus.y == bat.y:
                    bat.transport(wumpus, maze)
                    break
        hunter_dead = (hunter.x == wumpus.x and hunter.y == wumpus.y and wumpus.alive)
        return jsonify({
            "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo, "dead": hunter_dead},
            "wumpus": {"x": wumpus.x, "y": wumpus.y, "asleep": wumpus.asleep, "alive": wumpus.alive},
            "bats": [{"x": bat.x, "y": bat.y} for bat in superbats],
            "pits": [{"x": pit.x, "y": pit.y} for pit in pits]
        })

    @app.route('/handle_input', methods=['POST'])
    def handle_input():
        """
        Handles raw input from the client (WASD keys for movement, space for shooting).
        """
        key = request.json.get('key').lower()  # Get the key from the client request
        direction = None

        # Map WASD keys to directions
        if key == 'w':
            direction = 'up'
        elif key == 'a':
            direction = 'left'
        elif key == 's':
            direction = 'down'
        elif key == 'd':
            direction = 'right'
        elif key == ' ':  # Space key for shooting
            direction = 'shoot'

        if direction == 'shoot':
            result = hunter.shoot('up', maze)  # Example: shooting upward
            return jsonify({
                "result": result,
                "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo},
                "wumpus": {"x": wumpus.x, "y": wumpus.y, "asleep": wumpus.asleep, "alive": wumpus.alive}
            })
        elif direction:
            hunter.move(direction, maze)
            wumpus.move(hunter, maze)
            return jsonify({
                "hunter": {"x": hunter.x, "y": hunter.y, "ammo": hunter.ammo},
                "wumpus": {"x": wumpus.x, "y": wumpus.y, "asleep": wumpus.asleep, "alive": wumpus.alive}
            })
        else:
            return jsonify({"error": "Invalid key"})
        

    @app.route('/gameplay')
    def gameplay():
        """
        Renders the gameplay page and initializes game settings based on difficulty.
        """
        if 'user_id' not in session:
            flash('You must be logged in to access the game.', 'warning')
            return redirect(url_for('login'))
        
        difficulty = request.args.get('difficulty', 'easy')
        if difficulty == 'easy':
            multiplier = 1
            hunter_ammo = 5
            vision_radius = 3
            wumpus_speed = 2000
            wumpus_aggressive = False
            num_bats = 2
            num_pits = 2
        elif difficulty == 'medium':
            multiplier = 2
            hunter_ammo = 3
            vision_radius = 2
            wumpus_speed = 1500
            wumpus_aggressive = False
            num_bats = 4
            num_pits = 4
        elif difficulty == 'hard':
            multiplier = 3
            hunter_ammo = 1
            vision_radius = 1
            wumpus_speed = 500
            wumpus_aggressive = True
            num_bats = 10
            num_pits = 10

        session['hunter_ammo'] = hunter_ammo
        session['vision_radius'] = vision_radius
        session['wumpus_speed'] = wumpus_speed
        session['wumpus_aggressive'] = wumpus_aggressive
        session['difficulty'] = difficulty
        session['multiplier'] = multiplier
        session['num_bats'] = num_bats
        session['num_pits'] = num_pits

        return render_template(
            'Gameplay.html',
            hunter_ammo=hunter_ammo,
            vision_radius=vision_radius,
            wumpus_speed=wumpus_speed,
            wumpus_aggressive=wumpus_aggressive,
            difficulty=difficulty,
            multiplier_=multiplier
        )


    def update_leaderboard(username, time_taken, difficulty):
        """
        Updates the leaderboard with the given user's time if it is a new record.
        """
        conn = sqlite3.connect('HTW-2D/database/database.db')
        cursor = conn.cursor()
        # Check if a better time exists
        cursor.execute("SELECT time FROM leaderboard WHERE username=? AND difficulty=?", (username, difficulty))
        row = cursor.fetchone()
        if row is None or time_taken < float(row[0]):
            if row is None:
                cursor.execute("INSERT INTO leaderboard (username, time, difficulty) VALUES (?, ?, ?)", (username, time_taken, difficulty))
            else:
                cursor.execute("UPDATE leaderboard SET time=? WHERE username=? AND difficulty=?", (time_taken, username, difficulty))
            conn.commit()
        conn.close()

    @app.route('/submit_score', methods=['POST'])
    def submit_score():
        """
        Submits the game score (time taken) for the logged-in user.
        """
        data = request.json
        username = session.get('username', 'Anonymous')
        time_taken = float(data.get('time'))
        difficulty = data.get('difficulty')
        update_leaderboard(username, time_taken, difficulty)
        return jsonify({"success": True})

    @app.route('/leaderboard')
    def leaderboard():
        """
        Renders the leaderboard page with the top scores.
        """
        conn = sqlite3.connect('HTW-2D/database/database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT username, time, difficulty FROM leaderboard ORDER BY time ASC")
        rows = cursor.fetchall()
        conn.close()
        return render_template('Leaderboard.html', leaderboard=rows)