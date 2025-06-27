import random

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]  # 0 = wall, 1 = path

    def remove_dead_ends(self, min_exits=2):
        # Remove dead ends by connecting them to nearby paths.
        changed = True
        while changed:
            changed = False
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    if self.grid[y][x] == 1:
                        exits = 0
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            if self.grid[y+dy][x+dx] == 1:
                                exits += 1
                        if exits <= 1:
                            # Find a wall neighbor and punch through
                            neighbors = []
                            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                                nx, ny = x+dx, y+dy
                                if self.grid[ny][nx] == 0:
                                    neighbors.append((nx, ny))
                            if neighbors:
                                nx, ny = random.choice(neighbors)
                                self.grid[ny][nx] = 1
                                changed = True

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
        self.remove_dead_ends(min_exits=2)
        self.display_maze()

    def display_maze(self):
        for row in self.grid:
            print(" ".join(['#' if cell == 0 else '.' for cell in row]))

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
        print((self.x, self.y), "->", (new_x, new_y))
        self.x, self.y = new_x, new_y

    def shoot(self, direction, maze, wumpus):
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