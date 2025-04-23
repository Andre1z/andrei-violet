import pygame
import math
import random

# ----- Global Constants -----
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512
CELL_SIZE = 40        # Adjust so that maze fits nicely on the screen
WALL_THICKNESS = 3
BOT_RADIUS = 10
BOT_SPEED = 2.0
SENSOR_RANGE = 20
NUM_BOTS = 120
MUTATION_RATE = 0.1

# ----- Cell Class for Maze Generation -----
class Cell:
    def __init__(self, i, j):
        self.i = i  # column
        self.j = j  # row
        # Walls: [top, right, bottom, left]
        self.walls = [True, True, True, True]
        self.visited = False

# ----- Maze Class -----
class Maze:
    def __init__(self, width, height, cell_size, wall_thickness):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.wall_thickness = wall_thickness
        self.cols = width // cell_size
        self.rows = height // cell_size
        
        # Create grid of cells: grid[col][row]
        self.grid = [[Cell(i, j) for j in range(self.rows)] for i in range(self.cols)]
        self.generate_maze()
        self.walls = self.build_walls()
        self.exit = self.define_exit()

    def generate_maze(self):
        # Use recursive backtracking to carve out the maze
        stack = []
        current = self.grid[0][0]
        current.visited = True
        stack.append(current)

        while stack:
            current = stack[-1]
            next_cell = self.check_neighbors(current)
            if next_cell:
                next_cell.visited = True
                stack.append(next_cell)
                self.remove_walls(current, next_cell)
            else:
                stack.pop()

    def check_neighbors(self, cell):
        neighbors = []
        i, j = cell.i, cell.j
        # top neighbor
        if j - 1 >= 0 and not self.grid[i][j - 1].visited:
            neighbors.append(self.grid[i][j - 1])
        # right neighbor
        if i + 1 < self.cols and not self.grid[i + 1][j].visited:
            neighbors.append(self.grid[i + 1][j])
        # bottom neighbor
        if j + 1 < self.rows and not self.grid[i][j + 1].visited:
            neighbors.append(self.grid[i][j + 1])
        # left neighbor
        if i - 1 >= 0 and not self.grid[i - 1][j].visited:
            neighbors.append(self.grid[i - 1][j])
        return random.choice(neighbors) if neighbors else None

    def remove_walls(self, current, next_cell):
        dx = next_cell.i - current.i
        dy = next_cell.j - current.j
        # Remove wall between current and next cell
        if dx == 1:  # next is to the right
            current.walls[1] = False
            next_cell.walls[3] = False
        elif dx == -1:  # next is to the left
            current.walls[3] = False
            next_cell.walls[1] = False
        elif dy == 1:  # next is below
            current.walls[2] = False
            next_cell.walls[0] = False
        elif dy == -1:  # next is above
            current.walls[0] = False
            next_cell.walls[2] = False

    def build_walls(self):
        # Build a list of pygame.Rect objects for collision detection
        walls = []
        for j in range(self.rows):
            for i in range(self.cols):
                x = i * self.cell_size
                y = j * self.cell_size
                cell = self.grid[i][j]
                # Top wall
                if cell.walls[0]:
                    walls.append(pygame.Rect(x, y, self.cell_size, self.wall_thickness))
                # Right wall
                if cell.walls[1]:
                    walls.append(pygame.Rect(x + self.cell_size - self.wall_thickness, y, self.wall_thickness, self.cell_size))
                # Bottom wall
                if cell.walls[2]:
                    walls.append(pygame.Rect(x, y + self.cell_size - self.wall_thickness, self.cell_size, self.wall_thickness))
                # Left wall
                if cell.walls[3]:
                    walls.append(pygame.Rect(x, y, self.wall_thickness, self.cell_size))
        return walls

    def define_exit(self):
        # Define the exit as the inner area of the bottom-right cell.
        i = self.cols - 1
        j = self.rows - 1
        x = i * self.cell_size + self.wall_thickness
        y = j * self.cell_size + self.wall_thickness
        return pygame.Rect(x, y, self.cell_size - 2 * self.wall_thickness, self.cell_size - 2 * self.wall_thickness)

    def draw(self, screen):
        # Draw the maze walls
        for wall in self.walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)
        # Draw the exit area in green
        pygame.draw.rect(screen, (0, 255, 0), self.exit)

# ----- Bot Class -----
class Bot:
    def __init__(self, x, y, angle, weights=None):
        self.pos = [x, y]
        self.angle = angle  # in radians

        # Each bot has sensor weights for [front, left, right, left45, right45] and a bias.
        if weights is None:
            self.weights = {
                "front": random.uniform(-1, 1),
                "left": random.uniform(-1, 1),
                "right": random.uniform(-1, 1),
                "left45": random.uniform(-1, 1),
                "right45": random.uniform(-1, 1),
                "bias": random.uniform(-0.1, 0.1)
            }
        else:
            self.weights = weights

    def update(self, maze):
        # Sensor definitions: offsets in radians relative to the bot's current angle.
        sensor_angles = {
            "front": 0,
            "left": math.radians(90),
            "right": -math.radians(90),
            "left45": math.radians(45),
            "right45": -math.radians(45)
        }
        sensor_readings = {}
        # Get readings for each sensor
        for sensor, offset in sensor_angles.items():
            sensor_angle = self.angle + offset
            reading = self.get_sensor_reading(maze, sensor_angle)
            sensor_readings[sensor] = reading

        # Combine sensor readings using weights to determine steering adjustment.
        steering = (
            self.weights["bias"] +
            self.weights["front"] * sensor_readings["front"] +
            self.weights["left"] * sensor_readings["left"] +
            self.weights["right"] * sensor_readings["right"] +
            self.weights["left45"] * sensor_readings["left45"] +
            self.weights["right45"] * sensor_readings["right45"]
        )
        self.angle += steering * 0.1

        # Move the bot forward based on its heading.
        dx = BOT_SPEED * math.cos(self.angle)
        dy = BOT_SPEED * math.sin(self.angle)
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        # Check for collisions with maze walls.
        bot_rect = pygame.Rect(new_x - BOT_RADIUS, new_y - BOT_RADIUS, BOT_RADIUS * 2, BOT_RADIUS * 2)
        collision = any(bot_rect.colliderect(wall) for wall in maze.walls)
        if not collision:
            self.pos[0] = new_x
            self.pos[1] = new_y
        else:
            # On collision, adjust angle randomly.
            self.angle += random.uniform(-0.5, 0.5)

    def get_sensor_reading(self, maze, sensor_angle):
        """
        Cast a ray in the given sensor direction and return a normalized value:
        0 means no wall detected within range; values close to 1 indicate a nearby wall.
        """
        for distance in range(0, SENSOR_RANGE, 5):
            test_x = self.pos[0] + distance * math.cos(sensor_angle)
            test_y = self.pos[1] + distance * math.sin(sensor_angle)
            test_rect = pygame.Rect(test_x, test_y, 2, 2)
            for wall in maze.walls:
                if test_rect.colliderect(wall):
                    return (SENSOR_RANGE - distance) / SENSOR_RANGE
        return 0

    def draw(self, screen):
        # Draw the bot as a blue circle.
        pygame.draw.circle(screen, (0, 0, 255), (int(self.pos[0]), int(self.pos[1])), BOT_RADIUS)
        # Optionally, draw sensor rays in green.
        sensor_angles = {
            "front": 0,
            "left": math.radians(90),
            "right": -math.radians(90),
            "left45": math.radians(45),
            "right45": -math.radians(45)
        }
        for sensor, offset in sensor_angles.items():
            sensor_angle = self.angle + offset
            end_x = self.pos[0] + SENSOR_RANGE * math.cos(sensor_angle)
            end_y = self.pos[1] + SENSOR_RANGE * math.sin(sensor_angle)
            pygame.draw.line(screen, (0, 255, 0), self.pos, (end_x, end_y), 1)

# ----- Main Simulation Loop -----
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Random Maze Bots Evolution")
    clock = pygame.time.Clock()

    maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, WALL_THICKNESS)
    generation = 1

    # Start bots at the center of the top-left cell
    start_x = CELL_SIZE // 2
    start_y = CELL_SIZE // 2
    bots = [Bot(start_x, start_y, 0) for _ in range(NUM_BOTS)]
    winner = None

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        maze.draw(screen)

        for bot in bots:
            bot.update(maze)
            bot.draw(screen)
            # Check if the bot reached the exit area
            if maze.exit.collidepoint(bot.pos[0], bot.pos[1]):
                winner = bot

        pygame.display.flip()
        clock.tick(60)

        # When a bot wins, use its sensor weights to spawn the next generation with slight mutations.
        if winner is not None:
            print(f"Generation {generation} winner found!")
            new_bots = []
            for _ in range(NUM_BOTS):
                new_weights = {}
                for key, value in winner.weights.items():
                    new_weights[key] = value + random.uniform(-MUTATION_RATE, MUTATION_RATE)
                new_bots.append(Bot(start_x, start_y, 0, weights=new_weights))
            bots = new_bots
            generation += 1
            winner = None

    pygame.quit()

if __name__ == '__main__':
    main()
