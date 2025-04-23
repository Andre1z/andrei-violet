import pygame
import math
import random

# ----- Global Constants -----
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256
CELL_SIZE = 40        # Adjust so that maze fits nicely on the screen
WALL_THICKNESS = 3
BOT_SPEED = 2.0
MUTATION_RATE = 0.1  # Mutation factor for all bot parameters

# Default parameters for new bots
DEFAULT_SENSOR_RANGE = 20
DEFAULT_BOT_RADIUS = 10
DEFAULT_SENSOR_ANGLES = [
    0,                  # front
    math.radians(90),   # left
    -math.radians(90),  # right
    math.radians(45),   # left45
    -math.radians(45)   # right45
]

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
    def __init__(self, x, y, angle, sensor_angles=None, sensor_range=None, bot_radius=None, sensor_weights=None, bias=None):
        self.pos = [x, y]
        self.angle = angle  # in radians
        
        # Each bot has its own sensor configuration.
        # sensor_angles is a list of offsets (in radians) relative to the bot's current angle.
        self.sensor_angles = sensor_angles if sensor_angles is not None else DEFAULT_SENSOR_ANGLES.copy()
        self.sensor_range = sensor_range if sensor_range is not None else DEFAULT_SENSOR_RANGE
        self.bot_radius = bot_radius if bot_radius is not None else DEFAULT_BOT_RADIUS

        # Each bot has sensor weights corresponding to each sensor and a bias.
        if sensor_weights is None:
            self.sensor_weights = [random.uniform(-1, 1) for _ in range(len(self.sensor_angles))]
        else:
            self.sensor_weights = sensor_weights
        self.bias = bias if bias is not None else random.uniform(-0.1, 0.1)

    def update(self, maze):
        sensor_readings = []
        # Get readings for each sensor based on the bot's own sensor_angles and sensor_range.
        for offset in self.sensor_angles:
            sensor_angle = self.angle + offset
            reading = self.get_sensor_reading(maze, sensor_angle)
            sensor_readings.append(reading)
        # Combine sensor readings using the bot's own weights and bias.
        steering = self.bias
        for weight, reading in zip(self.sensor_weights, sensor_readings):
            steering += weight * reading
        self.angle += steering * 0.1

        # Move the bot forward based on its heading.
        dx = BOT_SPEED * math.cos(self.angle)
        dy = BOT_SPEED * math.sin(self.angle)
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        # Check for collisions with maze walls using the bot's own radius.
        bot_rect = pygame.Rect(new_x - self.bot_radius, new_y - self.bot_radius, self.bot_radius * 2, self.bot_radius * 2)
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
        for distance in range(0, int(self.sensor_range), 5):
            test_x = self.pos[0] + distance * math.cos(sensor_angle)
            test_y = self.pos[1] + distance * math.sin(sensor_angle)
            test_rect = pygame.Rect(test_x, test_y, 2, 2)
            for wall in maze.walls:
                if test_rect.colliderect(wall):
                    return (self.sensor_range - distance) / self.sensor_range
        return 0

    def draw(self, screen):
        # Draw the bot as a blue circle using its own bot_radius.
        pygame.draw.circle(screen, (0, 0, 255), (int(self.pos[0]), int(self.pos[1])), self.bot_radius)
        # Draw sensor rays in green.
        for offset in self.sensor_angles:
            sensor_angle = self.angle + offset
            end_x = self.pos[0] + self.sensor_range * math.cos(sensor_angle)
            end_y = self.pos[1] + self.sensor_range * math.sin(sensor_angle)
            pygame.draw.line(screen, (0, 255, 0), self.pos, (end_x, end_y), 1)

# ----- Main Simulation Loop -----
def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Random Maze Bots Evolution")
    clock = pygame.time.Clock()

    maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, WALL_THICKNESS)
    generation = 1

    # Start bots at the center of the top-left cell
    start_x = CELL_SIZE // 2
    start_y = CELL_SIZE // 2
    bots = [Bot(start_x, start_y, 0) for _ in range(120)]
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
        clock.tick(0)

        # When a bot wins, use its parameters to spawn the next generation with slight mutations.
        if winner is not None:
            print(f"Generation {generation} winner found!")
            new_bots = []
            for _ in range(120):
                # Mutate each parameter slightly.
                new_sensor_angles = [angle + random.uniform(-MUTATION_RATE, MUTATION_RATE) for angle in winner.sensor_angles]
                new_sensor_range = winner.sensor_range + random.uniform(-MUTATION_RATE * winner.sensor_range, MUTATION_RATE * winner.sensor_range)
                new_bot_radius = winner.bot_radius + random.uniform(-MUTATION_RATE * winner.bot_radius, MUTATION_RATE * winner.bot_radius)
                new_sensor_weights = [w + random.uniform(-MUTATION_RATE, MUTATION_RATE) for w in winner.sensor_weights]
                new_bias = winner.bias + random.uniform(-MUTATION_RATE, MUTATION_RATE)
                new_bots.append(Bot(start_x, start_y, 0,
                                    sensor_angles=new_sensor_angles,
                                    sensor_range=new_sensor_range,
                                    bot_radius=new_bot_radius,
                                    sensor_weights=new_sensor_weights,
                                    bias=new_bias))
            bots = new_bots

            # Every 20 generations, increase the maze (screen) size by 100 pixels in both dimensions.
            if generation % 20 == 0:
                SCREEN_WIDTH += 100
                SCREEN_HEIGHT += 100
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, WALL_THICKNESS)
                # Reset bot positions to the center of the top-left cell in the new maze.
                start_x = CELL_SIZE // 2
                start_y = CELL_SIZE // 2
                for bot in bots:
                    bot.pos = [start_x, start_y]

            generation += 1
            winner = None

    pygame.quit()

if __name__ == '__main__':
    main()
