import os
import sys
import ctypes
import pygame
import math
import random

# ----- Constantes Globales -----
SCREEN_WIDTH = 100
SCREEN_HEIGHT = 100
CELL_SIZE = 40        # Ajusta para que el laberinto se vea bien en pantalla
WALL_THICKNESS = 3
BOT_SPEED = 2.0
MUTATION_RATE = 0.1  # Factor de mutación para todos los parámetros del robot
NUMERO_BOTS = 250

# Parámetros por defecto para nuevos robots
DEFAULT_SENSOR_RANGE = 40
DEFAULT_BOT_RADIUS = 10
DEFAULT_SENSOR_ANGLES = [
    0,                  # frontal
    math.radians(90),   # izquierda
    -math.radians(90),  # derecha
    math.radians(45),   # izquierda45
    -math.radians(45)   # derecha45
]

# ----- Función para centrar la ventana -----
def center_window():
    wm_info = pygame.display.get_wm_info()
    # Para Windows, se usa ctypes para centrar la ventana
    if sys.platform == "win32":
        hwnd = wm_info.get('window')
        if hwnd:
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            x = (screen_width - SCREEN_WIDTH) // 2
            y = (screen_height - SCREEN_HEIGHT) // 2
            user32.SetWindowPos(hwnd, None, x, y, 0, 0, 0x0001)
    # Para otros sistemas, se puede usar:
    # os.environ['SDL_VIDEO_CENTERED'] = '1'

# ----- Clase Celda para la Generación del Laberinto -----
class Cell:
    def __init__(self, i, j):
        self.i = i  # columna
        self.j = j  # fila
        # Paredes: [arriba, derecha, abajo, izquierda]
        self.walls = [True, True, True, True]
        self.visited = False

# ----- Clase Laberinto -----
class Maze:
    def __init__(self, width, height, cell_size, wall_thickness):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.wall_thickness = wall_thickness
        self.cols = width // cell_size
        self.rows = height // cell_size
        
        # Crear una cuadrícula de celdas: grid[columna][fila]
        self.grid = [[Cell(i, j) for j in range(self.rows)] for i in range(self.cols)]
        self.generate_maze()
        self.walls = self.build_walls()
        self.exit = self.define_exit()

    def generate_maze(self):
        # Utiliza backtracking recursivo para tallar el laberinto
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
        # Vecino superior
        if j - 1 >= 0 and not self.grid[i][j - 1].visited:
            neighbors.append(self.grid[i][j - 1])
        # Vecino derecho
        if i + 1 < self.cols and not self.grid[i + 1][j].visited:
            neighbors.append(self.grid[i + 1][j])
        # Vecino inferior
        if j + 1 < self.rows and not self.grid[i][j + 1].visited:
            neighbors.append(self.grid[i][j + 1])
        # Vecino izquierdo
        if i - 1 >= 0 and not self.grid[i - 1][j].visited:
            neighbors.append(self.grid[i - 1][j])
        return random.choice(neighbors) if neighbors else None

    def remove_walls(self, current, next_cell):
        dx = next_cell.i - current.i
        dy = next_cell.j - current.j
        # Eliminar la pared entre la celda actual y la siguiente
        if dx == 1:  # siguiente está a la derecha
            current.walls[1] = False
            next_cell.walls[3] = False
        elif dx == -1:  # siguiente está a la izquierda
            current.walls[3] = False
            next_cell.walls[1] = False
        elif dy == 1:  # siguiente está abajo
            current.walls[2] = False
            next_cell.walls[0] = False
        elif dy == -1:  # siguiente está arriba
            current.walls[0] = False
            next_cell.walls[2] = False

    def build_walls(self):
        # Construir una lista de objetos pygame.Rect para la detección de colisiones
        walls = []
        for j in range(self.rows):
            for i in range(self.cols):
                x = i * self.cell_size
                y = j * self.cell_size
                cell = self.grid[i][j]
                # Pared superior
                if cell.walls[0]:
                    walls.append(pygame.Rect(x, y, self.cell_size, self.wall_thickness))
                # Pared derecha
                if cell.walls[1]:
                    walls.append(pygame.Rect(x + self.cell_size - self.wall_thickness, y, self.wall_thickness, self.cell_size))
                # Pared inferior
                if cell.walls[2]:
                    walls.append(pygame.Rect(x, y + self.cell_size - self.wall_thickness, self.cell_size, self.wall_thickness))
                # Pared izquierda
                if cell.walls[3]:
                    walls.append(pygame.Rect(x, y, self.wall_thickness, self.cell_size))
        return walls

    def define_exit(self):
        # Define la salida como el área interna de la celda inferior derecha.
        i = self.cols - 1
        j = self.rows - 1
        x = i * self.cell_size + self.wall_thickness
        y = j * self.cell_size + self.wall_thickness
        return pygame.Rect(x, y, self.cell_size - 2 * self.wall_thickness, self.cell_size - 2 * self.wall_thickness)

    def draw(self, screen):
        # Dibujar las paredes del laberinto
        for wall in self.walls:
            pygame.draw.rect(screen, (0, 0, 0), wall)
        # Dibujar el área de salida en verde
        pygame.draw.rect(screen, (0, 255, 0), self.exit)

# ----- Clase Bot (Robot) -----
class Bot:
    def __init__(self, x, y, angle, sensor_angles=None, sensor_range=None, bot_radius=None, sensor_weights=None, bias=None):
        self.pos = [x, y]
        self.angle = angle  # en radianes
        
        # Configuración de sensores
        self.sensor_angles = sensor_angles if sensor_angles is not None else DEFAULT_SENSOR_ANGLES.copy()
        self.sensor_range = sensor_range if sensor_range is not None else DEFAULT_SENSOR_RANGE
        self.bot_radius = bot_radius if bot_radius is not None else DEFAULT_BOT_RADIUS

        # Pesos de cada sensor y sesgo
        if sensor_weights is None:
            self.sensor_weights = [random.uniform(-1, 1) for _ in range(len(self.sensor_angles))]
        else:
            self.sensor_weights = sensor_weights
        self.bias = bias if bias is not None else random.uniform(-0.1, 0.1)

        # Memoria: conjunto de celdas visitadas, representadas como tuplas (i, j)
        self.visited_cells = set()

    def update(self, maze):
        # Registrar la celda actual en la memoria
        cell_i = int(self.pos[0] // maze.cell_size)
        cell_j = int(self.pos[1] // maze.cell_size)
        self.visited_cells.add((cell_i, cell_j))

        sensor_readings = []
        # Obtener lecturas de sensores modificadas con bonus/penalización por exploración
        for offset in self.sensor_angles:
            sensor_angle = self.angle + offset
            reading = self.get_sensor_reading(maze, sensor_angle)
            sensor_readings.append(reading)
        steering = self.bias
        for weight, reading in zip(self.sensor_weights, sensor_readings):
            steering += weight * reading
        self.angle += steering * 0.1

        # Calcular nueva posición
        dx = BOT_SPEED * math.cos(self.angle)
        dy = BOT_SPEED * math.sin(self.angle)
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy

        # Verificar colisiones con las paredes
        bot_rect = pygame.Rect(new_x - self.bot_radius, new_y - self.bot_radius,
                               self.bot_radius * 2, self.bot_radius * 2)
        collision = any(bot_rect.colliderect(wall) for wall in maze.walls)
        if not collision:
            self.pos[0] = new_x
            self.pos[1] = new_y
        else:
            # Ajustar el ángulo de forma aleatoria en caso de colisión
            self.angle += random.uniform(-0.5, 0.5)

    def get_sensor_reading(self, maze, sensor_angle):
        """
        Lanza un rayo en la dirección del sensor y combina la lectura de pared con un bonus
        basado en la exploración (memoria). Si el punto en el extremo del rayo está en una celda
        no visitada, se añade un bonus; si ya fue visitado, se penaliza.
        """
        # Detectar paredes a lo largo del rayo del sensor
        wall_reading = 0
        for distance in range(0, int(self.sensor_range), 5):
            test_x = self.pos[0] + distance * math.cos(sensor_angle)
            test_y = self.pos[1] + distance * math.sin(sensor_angle)
            test_rect = pygame.Rect(test_x, test_y, 2, 2)
            if any(test_rect.colliderect(wall) for wall in maze.walls):
                wall_reading = (self.sensor_range - distance) / self.sensor_range
                break

        # Calcular bonus de novedad:
        # Se toma el punto en el extremo del sensor y se determina la celda correspondiente.
        tip_x = self.pos[0] + self.sensor_range * math.cos(sensor_angle)
        tip_y = self.pos[1] + self.sensor_range * math.sin(sensor_angle)
        cell_i = int(tip_x // maze.cell_size)
        cell_j = int(tip_y // maze.cell_size)
        if 0 <= cell_i < maze.cols and 0 <= cell_j < maze.rows:
            if (cell_i, cell_j) not in self.visited_cells:
                novelty_value = 0.0   # Bonus para zona no explorada
            else:
                novelty_value = -0.0 # Penalización para zona ya explorada
        else:
            novelty_value = -0.0      # Fuera del laberinto

        # Se modula el bonus según lo “abierta” que esté la trayectoria (si hay pared, se reduce)
        novelty_bonus = (1 - wall_reading) * novelty_value
        return wall_reading + novelty_bonus

    def draw(self, screen):
        # Dibujar el bot como un círculo azul
        pygame.draw.circle(screen, (0, 0, 255), (int(self.pos[0]), int(self.pos[1])), self.bot_radius)
        # Dibujar los rayos de los sensores en verde
        for offset in self.sensor_angles:
            sensor_angle = self.angle + offset
            end_x = self.pos[0] + self.sensor_range * math.cos(sensor_angle)
            end_y = self.pos[1] + self.sensor_range * math.sin(sensor_angle)
            pygame.draw.line(screen, (0, 255, 0), self.pos, (end_x, end_y), 1)

# ----- Bucle Principal de Simulación -----
def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT,NUMERO_BOTS
    pygame.init()
    
    # Centrar la ventana
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    center_window()
    clock = pygame.time.Clock()

    maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, WALL_THICKNESS)
    generation = 1

    start_x = CELL_SIZE // 2
    start_y = CELL_SIZE // 2
    bots = [Bot(start_x, start_y, 0) for _ in range(NUMERO_BOTS)]
    winner = None

    running = True
    while running:
        pygame.display.set_caption("Generación: " + str(generation))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        maze.draw(screen)

        for bot in bots:
            bot.update(maze)
            bot.draw(screen)
            # Comprobar si el robot alcanzó el área de salida
            if maze.exit.collidepoint(bot.pos[0], bot.pos[1]):
                winner = bot

        pygame.display.flip()
        clock.tick(60)

        # Cuando un robot gana, se usa su configuración (con mutaciones) para la siguiente generación.
        if winner is not None:
            print(f"¡Ganador de la generación {generation} encontrado!")
            new_bots = []
            for _ in range(NUMERO_BOTS):
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

            # Cada generación se aumenta el tamaño del laberinto y se reinicia la posición de los bots.
            if generation % 1 == 0:
                if NUMERO_BOTS > 0:
                    NUMERO_BOTS -= 1
                if SCREEN_HEIGHT < 1080:
                    SCREEN_WIDTH += 4
                    SCREEN_HEIGHT += 4
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                center_window()
                maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, WALL_THICKNESS)
                start_x = CELL_SIZE // 2
                start_y = CELL_SIZE // 2
                for bot in bots:
                    bot.pos = [start_x, start_y]

            generation += 1
            winner = None

    pygame.quit()

if __name__ == '__main__':
    main()
