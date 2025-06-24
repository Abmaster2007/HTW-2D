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
        def is_valid_cell(x, y):
            return 0 <= x < self.width and 0 <= y < self.height and self.grid[y][x] == 0

        def carve_path(x, y):
            self.grid[y][x] = 1  # Mark the current cell as a path
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Up, Down, Left, Right
            random.shuffle(directions)  # Randomize directions

            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2  # Move two steps in the chosen direction
                if is_valid_cell(nx, ny):
                    self.grid[y + dy][x + dx] = 1  # Carve path between current and next cell
                    carve_path(nx, ny)  # Recursively carve the next cell

        # Start carving from the top-left corner
        carve_path(1, 1)

    def get_maze(self):
        return self.grid

class Hunter:
    def __init__(self, x, y, ammo=5):
        self.x = x
        self.y = y
        self.ammo = ammo

    def move(self, direction, maze):
        new_x, new_y = self.x, self.y
        if direction == "up" and self.y > 0 and maze[self.y - 1][self.x] == 1:
            new_y -= 1
        elif direction == "down" and self.y < len(maze) - 1 and maze[self.y + 1][self.x] == 1:
            new_y += 1
        elif direction == "left" and self.x > 0 and maze[self.y][self.x - 1] == 1:
            new_x -= 1
        elif direction == "right" and self.x < len(maze[0]) - 1 and maze[self.y][self.x + 1] == 1:
            new_x += 1

        self.x, self.y = new_x, new_y

    def shoot(self, direction, maze):
        if self.ammo > 0:
            self.ammo -= 1  # Reduce ammo count
            dx, dy = 0, 0

            # Determine shooting direction
            if direction == "up":
                dx, dy = 0, -1
            elif direction == "down":
                dx, dy = 0, 1
            elif direction == "left":
                dx, dy = -1, 0
            elif direction == "right":
                dx, dy = 1, 0

            # Check if Wumpus is hit
            x, y = self.x, self.y
            while 0 <= x < len(maze[0]) and 0 <= y < len(maze):
                if x == wumpus.x and y == wumpus.y:
                    wumpus.alive = False  # Kill the Wumpus
                    return "Wumpus defeated!"
                if maze[y][x] == 0:  # Stop if hitting a wall
                    break
                x += dx
                y += dy

            return "Missed!"
        return "No ammo left"


class Wumpus:
    def __init__(self, x, y, asleep=True):
        self.x = x
        self.y = y
        self.asleep = asleep
        self.alive = True

    def move(self, hunter, maze):
        if not self.alive or self.asleep:
            return
        path = self.bfs((self.x, self.y), (hunter.x, hunter.y), maze)
        if path and len(path) > 1:
            self.x, self.y = path[1]
    
    def bfs(self, start, goal, maze):
        width, height = len(maze[0]), len(maze)
        queue = [(start, [start])]
        visited = set()
        visited.add(start)
        while queue:
            (x, y), path = queue.pop(0)
            if (x, y) == goal:
                return path
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        return None  # No path found

class SuperBat:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def transport(self, entity, maze):
        # entity: Hunter or Wumpus
        valid_cells = [(x, y) for y in range(len(maze)) for x in range(len(maze[0])) if maze[y][x] == 1]
        new_x, new_y = random.choice(valid_cells)
        entity.x = new_x
        entity.y = new_y
        return (new_x, new_y)

class BottomlessPit:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def check_fall(self, hunter):
        # If hunter steps on the pit, he dies
        return hunter.x == self.x and hunter.y == self.y

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    conn = sqlite3.connect('HTW-2D/database/database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT username, time, difficulty FROM leaderboard ORDER BY time ASC")
    rows = cursor.fetchall()
    conn.close()
    return render_template('Gamemenu.html', leaderboard=rows)

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

# Initialize game state
maze = [[random.choice([0, 1]) for _ in range(21)] for _ in range(11)]
hunter = Hunter(0, 0)  # Create an instance of the Hunter class
wumpus = Wumpus(10, 10)  # Create an instance of the Wumpus class
superbats = []  # List to store SuperBat instances
pits = []  # List to store BottomlessPit instances

@app.route('/initialize', methods=['GET'])
def initialize_game():
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
    direction = request.json.get('direction')  # Get shooting direction from the client
    result = hunter.shoot(direction, maze)
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
        multiplier=multiplier
    )


def update_leaderboard(username, time_taken, difficulty):
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
    data = request.json
    username = session.get('username', 'Anonymous')
    time_taken = float(data.get('time'))
    difficulty = data.get('difficulty')
    update_leaderboard(username, time_taken, difficulty)
    return jsonify({"success": True})

@app.route('/leaderboard')
def leaderboard():
    conn = sqlite3.connect('HTW-2D/database/database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT username, time, difficulty FROM leaderboard ORDER BY time ASC")
    rows = cursor.fetchall()
    conn.close()
    return render_template('Leaderboard.html', leaderboard=rows)

if __name__ == '__main__':
    app.run(debug=True)