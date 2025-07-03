"""
models.py

Contains the core classes for the Hunt the Wumpus game logic, including Maze, Hunter, Wumpus, SuperBat, and BottomlessPit.
"""

import random

class Maze:
    """
    Represents the game maze.
    Attributes:
        width (int): Width of the maze.
        height (int): Height of the maze.
        grid (list): 2D list representing the maze structure (0 = wall, 1 = path).
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def remove_dead_ends(self, min_exits=2):
        """
        Removes dead ends from the maze by ensuring each path cell has at least min_exits exits.
        """
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
        """
        Generates the maze layout using a maze generation algorithm.
        """
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
        """
        Prints the maze to the console for debugging.
        """
        for row in self.grid:
            print(" ".join(['#' if cell == 0 else '.' for cell in row]))

    def get_maze(self):
        """
        Returns the maze grid.
        """
        return self.grid

class Hunter:
    """
    Represents the player character.
    Attributes:
        x (int): X position.
        y (int): Y position.
        ammo (int): Number of arrows.
    """
    def __init__(self, x, y, ammo=5):
        self.x = x
        self.y = y
        self.ammo = ammo

    def move(self, direction, maze):
        """
        Moves the hunter in the specified direction if possible.
        """
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
        """
        Shoots an arrow in the specified direction.
        """
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
    """
    Represents the Wumpus enemy.
    Attributes:
        x (int): X position.
        y (int): Y position.
        asleep (bool): Whether the Wumpus is asleep.
        alive (bool): Whether the Wumpus is alive.
    """
    def __init__(self, x, y, asleep=True):
        self.x = x
        self.y = y
        self.asleep = asleep
        self.alive = True

    def move(self, hunter, maze):
        """
        Moves the Wumpus towards the hunter or randomly, depending on game logic.
        """
        if not self.alive or self.asleep:
            return
        path = self.bfs((self.x, self.y), (hunter.x, hunter.y), maze)
        if path and len(path) > 1:
            self.x, self.y = path[1]
    
    def bfs(self, start, goal, maze):
        """
        Breadth-first search for pathfinding, reusing similar pattern from the previous project.
        Returns a path from start to goal if one exists.
        """
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
    """
    Represents a SuperBat that can transport entities.
    Attributes:
        x (int): X position.
        y (int): Y position.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def transport(self, entity, maze):
        """
        Transports the given entity to a random valid location in the maze.
        """
        # entity: Hunter or Wumpus
        valid_cells = [(x, y) for y in range(len(maze)) for x in range(len(maze[0])) if maze[y][x] == 1]
        new_x, new_y = random.choice(valid_cells)
        entity.x = new_x
        entity.y = new_y
        return (new_x, new_y)

class BottomlessPit:
    """
    Represents a bottomless pit hazard.
    Attributes:
        x (int): X position.
        y (int): Y position.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def check_fall(self, hunter):
        """
        Checks if the hunter has fallen into the pit.
        """
        # If hunter steps on the pit, he dies
        return hunter.x == self.x and hunter.y == self.y