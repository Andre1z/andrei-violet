import pygame
import math
import random

# ----- Global Constants -----
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOT_RADIUS = 10
BOT_SPEED = 2.0
SENSOR_RANGE = 50
NUM_BOTS = 20
MUTATION_RATE = 0.1

# ----- Maze Class -----
class Maze:
    def __init__(self):
        # Define outer boundaries as walls
        self.walls = []
        self.walls.append(pygame.Rect(0, 0, SCREEN_WIDTH, 10))             # Top wall
        self.walls.append(pygame.Rect(0, 0, 10, SCREEN_HEIGHT))            # Left wall
        self.walls.append(pygame.Rect(0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10))  # Bottom wall
        self.walls.append(pygame.Rect(SCREEN_WIDTH - 10, 0, 10, SCREEN_HEIGHT))  # Right wall

        # Create some inner walls manually (you can expand this to generate more complex mazes)
        self.walls.append(pygame.Rect(200, 0, 10, 400))
        self.walls.append(pygame.Rect(400, 200, 10, 400))
        self.walls.append(pygame.Rect(600, 0, 10, 400))
        self.walls.append(pygame.Rect(200, 400, 210, 10))

        # Define an exit area – a rectangle at the far right of the maze
        self.exit = pygame.Rect(SCREEN_WIDTH - 40, SCREEN_HEIGHT - 60, 30, 50)

    def draw(self, screen):
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)
        # Draw the exit area in a different color (e.g. green)
        pygame.draw.rect(screen, (0, 255, 0), self.exit)

# ----- Bot Class -----
class Bot:
    def __init__(self, x, y, angle, weights=None):
        self.pos = [x, y]
        self.angle = angle  # in radians

        # Each bot has a set of sensor weights (for front, left, right, left45, right45) and a bias term.
        # These parameters determine how sensor readings affect turning.
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
        # Sensor definitions: angle offsets relative to the bot's current heading
        sensor_angles = {
            "front": 0,
            "left": math.radians(90),
            "right": -math.radians(90),
            "left45": math.radians(45),
            "right45": -math.radians(45)
        }
        sensor_readings = {}
        # Compute sensor reading for each sensor
        for sensor, offset in sensor_angles.items():
            sensor_angle = self.angle + offset
            reading = self.get_sensor_reading(maze, sensor_angle)
            sensor_readings[sensor] = reading

        # Combine sensor readings into a steering command using the bot's weights.
        # (A higher sensor reading means the wall is closer.)
        steering = (
            self.weights["bias"] +
            self.weights["front"] * sensor_readings["front"] +
            self.weights["left"] * sensor_readings["left"] +
            self.weights["right"] * sensor_readings["right"] +
            self.weights["left45"] * sensor_readings["left45"] +
            self.weights["right45"] * sensor_readings["right45"]
        )
        # Adjust bot's heading – scaling factor determines how sharply it turns.
        self.angle += steering * 0.1

        # Calculate new position by moving forward at a constant speed.
        dx = BOT_SPEED * math.cos(self.angle)
        dy = BOT_SPEED * math.sin(self.angle)
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        # Check if the new position would collide with any wall
        bot_rect = pygame.Rect(new_x - BOT_RADIUS, new_y - BOT_RADIUS, BOT_RADIUS * 2, BOT_RADIUS * 2)
        collision = any(bot_rect.colliderect(wall) for wall in maze.walls)
        if not collision:
            self.pos[0] = new_x
            self.pos[1] = new_y
        else:
            # If a collision is about to happen, adjust the angle randomly to avoid the wall.
            self.angle += random.uniform(-0.5, 0.5)

    def get_sensor_reading(self, maze, sensor_angle):
        """
        Cast a ray in the sensor direction and return a normalized reading:
        0 means no wall within range; values approaching 1 mean the wall is very near.
        """
        # Step along the ray in increments (here, 5 pixels)
        for distance in range(0, SENSOR_RANGE, 5):
            test_x = self.pos[0] + distance * math.cos(sensor_angle)
            test_y = self.pos[1] + distance * math.sin(sensor_angle)
            test_rect = pygame.Rect(test_x, test_y, 2, 2)
            for wall in maze.walls:
                if test_rect.colliderect(wall):
                    # Normalize the reading so that closer distances yield higher values.
                    return (SENSOR_RANGE - distance) / SENSOR_RANGE
        return 0  # no wall detected within range

    def draw(self, screen):
        # Draw the bot as a blue circle
        pygame.draw.circle(screen, (0, 0, 255), (int(self.pos[0]), int(self.pos[1])), BOT_RADIUS)
        # Optionally, draw the sensor rays (in green)
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
    pygame.display.set_caption("Maze Bots Evolution")
    clock = pygame.time.Clock()

    maze = Maze()
    generation = 1
    # Initialize bots at a start position (for example, near the top-left)
    bots = [Bot(50, 50, 0) for _ in range(NUM_BOTS)]
    winner = None

    running = True
    while running:
        # Handle events (quit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw background and maze
        screen.fill((255, 255, 255))
        maze.draw(screen)

        # Update and draw each bot
        for bot in bots:
            bot.update(maze)
            bot.draw(screen)
            # Check if bot has reached the exit area
            if maze.exit.collidepoint(bot.pos[0], bot.pos[1]):
                winner = bot

        pygame.display.flip()
        clock.tick(60)

        # When a winner is found, use its sensor weights as the basis for the next generation
        if winner is not None:
            print(f"Generation {generation} winner found!")
            new_bots = []
            for _ in range(NUM_BOTS):
                new_weights = {}
                # Apply slight mutations to each sensor weight and bias
                for key, value in winner.weights.items():
                    new_value = value + random.uniform(-MUTATION_RATE, MUTATION_RATE)
                    new_weights[key] = new_value
                # Spawn new bot at the starting position with mutated parameters
                new_bots.append(Bot(50, 50, 0, weights=new_weights))
            bots = new_bots
            generation += 1
            winner = None

    pygame.quit()

if __name__ == '__main__':
    main()
