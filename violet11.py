import cv2
import numpy as np
import math
import random
from concurrent.futures import ProcessPoolExecutor

# ----- Global Constants -----
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
CELL_SIZE = 40
WALL_THICKNESS = 3
BOT_SPEED = 2.0
MUTATION_RATE = 0.1
NUMERO_BOTS = 250

DEFAULT_SENSOR_RANGE = 40
DEFAULT_BOT_RADIUS = 10
DEFAULT_SENSOR_ANGLES = [
    0,                  # frontal
    math.radians(90),   # left
    -math.radians(90),  # right
    math.radians(45),   # left45
    -math.radians(45)   # right45
]

# ----- Maze, Cell, and Bot Classes (with similar logic as before) -----
# Note: You need to include your maze generation and bot update logic.
# For parallelization, ensure you add methods like `to_dict` and `from_dict` for state serialization.

class Cell:
    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.walls = [True, True, True, True]  # [up, right, down, left]
        self.visited = False

class Maze:
    def __init__(self, width, height, cell_size, wall_thickness):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.wall_thickness = wall_thickness
        self.cols = width // cell_size
        self.rows = height // cell_size
        self.grid = [[Cell(i, j) for j in range(self.rows)] for i in range(self.cols)]
        self.generate_maze()
        self.walls = self.build_walls()
        self.exit = self.define_exit()

    def generate_maze(self):
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
        if j - 1 >= 0 and not self.grid[i][j - 1].visited:
            neighbors.append(self.grid[i][j - 1])
        if i + 1 < self.cols and not self.grid[i + 1][j].visited:
            neighbors.append(self.grid[i + 1][j])
        if j + 1 < self.rows and not self.grid[i][j + 1].visited:
            neighbors.append(self.grid[i][j + 1])
        if i - 1 >= 0 and not self.grid[i - 1][j].visited:
            neighbors.append(self.grid[i - 1][j])
        return random.choice(neighbors) if neighbors else None

    def remove_walls(self, current, next_cell):
        dx = next_cell.i - current.i
        dy = next_cell.j - current.j
        if dx == 1:
            current.walls[1] = False
            next_cell.walls[3] = False
        elif dx == -1:
            current.walls[3] = False
            next_cell.walls[1] = False
        elif dy == 1:
            current.walls[2] = False
            next_cell.walls[0] = False
        elif dy == -1:
            current.walls[0] = False
            next_cell.walls[2] = False

    def build_walls(self):
        walls = []
        for j in range(self.rows):
            for i in range(self.cols):
                x = i * self.cell_size
                y = j * self.cell_size
                cell = self.grid[i][j]
                if cell.walls[0]:
                    walls.append((x, y, self.cell_size, self.wall_thickness))
                if cell.walls[1]:
                    walls.append((x + self.cell_size - self.wall_thickness, y, self.wall_thickness, self.cell_size))
                if cell.walls[2]:
                    walls.append((x, y + self.cell_size - self.wall_thickness, self.cell_size, self.wall_thickness))
                if cell.walls[3]:
                    walls.append((x, y, self.wall_thickness, self.cell_size))
        return walls

    def define_exit(self):
        i = self.cols - 1
        j = self.rows - 1
        x = i * self.cell_size + self.wall_thickness
        y = j * self.cell_size + self.wall_thickness
        return (x, y, self.cell_size - 2 * self.wall_thickness, self.cell_size - 2 * self.wall_thickness)

    def to_dict(self):
        return {
            "walls": self.walls,
            "cell_size": self.cell_size,
            "cols": self.cols,
            "rows": self.rows,
            "exit": self.exit
        }

class Bot:
    def __init__(self, x, y, angle, sensor_angles=None, sensor_range=None, bot_radius=None, sensor_weights=None, bias=None):
        self.pos = [x, y]
        self.angle = angle
        self.sensor_angles = sensor_angles if sensor_angles is not None else DEFAULT_SENSOR_ANGLES.copy()
        self.sensor_range = sensor_range if sensor_range is not None else DEFAULT_SENSOR_RANGE
        self.bot_radius = bot_radius if bot_radius is not None else DEFAULT_BOT_RADIUS
        if sensor_weights is None:
            self.sensor_weights = [random.uniform(-1, 1) for _ in range(len(self.sensor_angles))]
        else:
            self.sensor_weights = sensor_weights
        self.bias = bias if bias is not None else random.uniform(-0.1, 0.1)
        self.visited_cells = set()

    def to_dict(self):
        return {
            "pos": self.pos,
            "angle": self.angle,
            "sensor_angles": self.sensor_angles,
            "sensor_range": self.sensor_range,
            "bot_radius": self.bot_radius,
            "sensor_weights": self.sensor_weights,
            "bias": self.bias,
            "visited_cells": list(self.visited_cells)
        }

    def from_dict(self, state):
        self.pos = state["pos"]
        self.angle = state["angle"]
        self.sensor_angles = state["sensor_angles"]
        self.sensor_range = state["sensor_range"]
        self.bot_radius = state["bot_radius"]
        self.sensor_weights = state["sensor_weights"]
        self.bias = state["bias"]
        self.visited_cells = set(state["visited_cells"])

# ----- Utility Functions for Parallel Updates -----
def rect_colliderect(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return not (x1 + w1 <= x2 or x1 >= x2 + w2 or y1 + h1 <= y2 or y1 >= y2 + h2)

def get_sensor_reading(state, maze_data, sensor_angle):
    wall_reading = 0
    for distance in range(0, int(state['sensor_range']), 5):
        test_x = state['pos'][0] + distance * math.cos(sensor_angle)
        test_y = state['pos'][1] + distance * math.sin(sensor_angle)
        test_rect = (test_x, test_y, 2, 2)
        if any(rect_colliderect(test_rect, wall) for wall in maze_data['walls']):
            wall_reading = (state['sensor_range'] - distance) / state['sensor_range']
            break
    tip_x = state['pos'][0] + state['sensor_range'] * math.cos(sensor_angle)
    tip_y = state['pos'][1] + state['sensor_range'] * math.sin(sensor_angle)
    cell_i = int(tip_x // maze_data['cell_size'])
    cell_j = int(tip_y // maze_data['cell_size'])
    if 0 <= cell_i < maze_data['cols'] and 0 <= cell_j < maze_data['rows']:
        if (cell_i, cell_j) not in state['visited_cells']:
            novelty_value = 0.0  # bonus for unexplored cell
        else:
            novelty_value = -0.0
    else:
        novelty_value = -0.0
    novelty_bonus = (1 - wall_reading) * novelty_value
    return wall_reading + novelty_bonus

def update_bot_state(state, maze_data):
    # Update visited cells
    cell_i = int(state['pos'][0] // maze_data['cell_size'])
    cell_j = int(state['pos'][1] // maze_data['cell_size'])
    visited = set(state['visited_cells'])
    visited.add((cell_i, cell_j))
    state['visited_cells'] = list(visited)
    
    # Sensor readings and update
    sensor_readings = []
    for offset in state['sensor_angles']:
        sensor_angle = state['angle'] + offset
        reading = get_sensor_reading(state, maze_data, sensor_angle)
        sensor_readings.append(reading)
    steering = state['bias']
    for weight, reading in zip(state['sensor_weights'], sensor_readings):
        steering += weight * reading
    state['angle'] += steering * 0.1

    dx = BOT_SPEED * math.cos(state['angle'])
    dy = BOT_SPEED * math.sin(state['angle'])
    new_x = state['pos'][0] + dx
    new_y = state['pos'][1] + dy

    bot_rect = (new_x - state['bot_radius'], new_y - state['bot_radius'],
                state['bot_radius'] * 2, state['bot_radius'] * 2)
    collision = any(rect_colliderect(bot_rect, wall) for wall in maze_data['walls'])
    if not collision:
        state['pos'] = [new_x, new_y]
    else:
        state['angle'] += random.uniform(-0.5, 0.5)
    return state

# ----- OpenCV Drawing Functions -----
def draw_maze(img, maze):
    # Draw maze walls as black rectangles
    for wall in maze.walls:
        x, y, w, h = wall
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)
    # Draw the exit area in green
    ex, ey, ew, eh = maze.exit
    cv2.rectangle(img, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), -1)

def draw_bot(img, bot):
    x, y = int(bot.pos[0]), int(bot.pos[1])
    cv2.circle(img, (x, y), bot.bot_radius, (255, 0, 0), -1)
    for offset in bot.sensor_angles:
        sensor_angle = bot.angle + offset
        end_x = int(bot.pos[0] + bot.sensor_range * math.cos(sensor_angle))
        end_y = int(bot.pos[1] + bot.sensor_range * math.sin(sensor_angle))
        cv2.line(img, (x, y), (end_x, end_y), (0, 255, 0), 1)

# ----- Main Simulation Loop Using OpenCV for Rendering -----
def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, NUMERO_BOTS
    maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, WALL_THICKNESS)
    generation = 1
    start_x = CELL_SIZE // 2
    start_y = CELL_SIZE // 2
    bots = [Bot(start_x, start_y, 0) for _ in range(NUMERO_BOTS)]
    winner = None

    # Create a ProcessPoolExecutor for parallel bot updates
    with ProcessPoolExecutor() as executor:
        while True:
            # Create a blank white image
            img = np.ones((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8) * 255

            # Draw maze on the image
            draw_maze(img, maze)
            
            # Serialize maze and bot states
            maze_data = maze.to_dict()
            bot_states = [bot.to_dict() for bot in bots]
            
            # Parallel update of bot states
            updated_states = list(executor.map(lambda state: update_bot_state(state, maze_data), bot_states))
            for bot, state in zip(bots, updated_states):
                bot.from_dict(state)
                draw_bot(img, bot)
                # Check for win condition (bot reaching the exit)
                ex, ey, ew, eh = maze.exit
                if ex <= bot.pos[0] <= ex + ew and ey <= bot.pos[1] <= ey + eh:
                    winner = bot
            
            # Display the simulation frame using OpenCV
            cv2.imshow("Simulation", img)
            key = cv2.waitKey(1)
            if key == 27:  # ESC key to exit
                break

            # Generation update when a bot wins
            if winner is not None:
                print(f"Generation {generation} winner found!")
                new_bots = []
                for _ in range(NUMERO_BOTS):
                    new_sensor_angles = [angle + random.uniform(-MUTATION_RATE, MUTATION_RATE)
                                           for angle in winner.sensor_angles]
                    new_sensor_range = winner.sensor_range + random.uniform(-MUTATION_RATE * winner.sensor_range,
                                                                           MUTATION_RATE * winner.sensor_range)
                    new_bot_radius = winner.bot_radius + random.uniform(-MUTATION_RATE * winner.bot_radius,
                                                                       MUTATION_RATE * winner.bot_radius)
                    new_sensor_weights = [w + random.uniform(-MUTATION_RATE, MUTATION_RATE)
                                          for w in winner.sensor_weights]
                    new_bias = winner.bias + random.uniform(-MUTATION_RATE, MUTATION_RATE)
                    new_bots.append(Bot(start_x, start_y, 0,
                                        sensor_angles=new_sensor_angles,
                                        sensor_range=new_sensor_range,
                                        bot_radius=new_bot_radius,
                                        sensor_weights=new_sensor_weights,
                                        bias=new_bias))
                bots = new_bots
                # Optionally adjust simulation parameters (maze size, etc.)
                generation += 1
                winner = None

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
