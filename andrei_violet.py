#!/usr/bin/env python3
"""
andrei_violet.py

Proyecto: andrei-violet
Descripción: Este script integra la generación de laberintos, la simulación gráfica
usando Pygame y el control de un agente dentro del laberinto. Todo se encuentra en
un único archivo para facilitar la prueba y futura portabilidad a otros lenguajes.
"""

import pygame
import sys
import random

# ---------------------------------------------------
# Configuración Global
# ---------------------------------------------------
CELL_SIZE = 40          # Tamaño de cada celda (en píxeles)
WIDTH = 800             # Ancho de la ventana
HEIGHT = 600            # Alto de la ventana
FPS = 30                # Frames por segundo

ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

# Colores (en formato RGB)
WALL_COLOR = (50, 50, 50)    # Color para los muros
PATH_COLOR = (200, 200, 200) # Color para los caminos
AGENT_COLOR = (255, 0, 0)    # Color para el agente (rojo)

# ---------------------------------------------------
# Clase Maze: Generación y dibujo del laberinto
# ---------------------------------------------------
class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # Inicializa la grilla con 1 (muro) en todas las celdas
        self.grid = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def generate_maze(self):
        """
        Genera el laberinto utilizando backtracking recursivo.
        La idea es saltear celdas de 2 en 2 para mantener un muro entre caminos.
        """
        visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        stack = []

        # Comenzamos en la celda (0,0)
        r, c = 0, 0
        visited[r][c] = True
        self.grid[r][c] = 0

        while True:
            neighbours = []
            # Definimos las 4 direcciones (arriba, abajo, izquierda, derecha)
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                nr, nc = r + dr * 2, c + dc * 2
                if 0 <= nr < self.rows and 0 <= nc < self.cols and not visited[nr][nc]:
                    neighbours.append((nr, nc, dr, dc))
            
            if neighbours:
                # Elegir un vecino aleatoriamente
                nr, nc, dr, dc = random.choice(neighbours)
                # Quitar el muro intermedio
                self.grid[r + dr][c + dc] = 0
                self.grid[nr][nc] = 0
                visited[nr][nc] = True
                stack.append((r, c))
                r, c = nr, nc
            elif stack:
                r, c = stack.pop()
            else:
                break

    def draw(self, surface):
        """
        Dibuja el laberinto en la superficie pasada como parámetro.
        Cada celda se representa mediante un rectángulo.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[row][col] == 1:
                    pygame.draw.rect(surface, WALL_COLOR, rect)
                else:
                    pygame.draw.rect(surface, PATH_COLOR, rect)

# ---------------------------------------------------
# Clase Agent: Movimiento y dibujo del agente
# ---------------------------------------------------
class Agent:
    def __init__(self, maze):
        self.maze = maze
        # Posición inicial en la celda (0,0)
        self.row = 0
        self.col = 0

    def move(self, drow, dcol):
        """
        Mueve el agente en la dirección indicada si la celda destino es un camino.
        drow: cambio en filas (-1 sube, +1 baja)
        dcol: cambio en columnas (-1 a la izquierda, +1 a la derecha)
        """
        new_row = self.row + drow
        new_col = self.col + dcol
        if 0 <= new_row < self.maze.rows and 0 <= new_col < self.maze.cols:
            if self.maze.grid[new_row][new_col] == 0:
                self.row = new_row
                self.col = new_col

    def handle_key(self, event):
        """Procesa los eventos de teclado para mover el agente."""
        if event.key == pygame.K_UP:
            self.move(-1, 0)
        elif event.key == pygame.K_DOWN:
            self.move(1, 0)
        elif event.key == pygame.K_LEFT:
            self.move(0, -1)
        elif event.key == pygame.K_RIGHT:
            self.move(0, 1)

    def draw(self, surface):
        """
        Dibuja el agente sobre la superficie de Pygame.
        El agente se representa como un rectángulo rojo en la celda en la que se encuentra.
        """
        rect = pygame.Rect(self.col * CELL_SIZE, self.row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, AGENT_COLOR, rect)

# ---------------------------------------------------
# Función para manejar eventos
# ---------------------------------------------------
def handle_events(agent):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            agent.handle_key(event)

# ---------------------------------------------------
# Función Principal: Configuración y ejecución de la simulación
# ---------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("andrei-violet: Simulación de Laberinto")
    clock = pygame.time.Clock()

    # Crear y generar el laberinto
    maze = Maze(ROWS, COLS)
    maze.generate_maze()

    # Crear el agente y posicionarlo en el laberinto
    agent = Agent(maze)

    # Bucle principal de la simulación
    while True:
        handle_events(agent)

        # Actualización y renderizado
        screen.fill((0, 0, 0))  # Fondo negro
        maze.draw(screen)
        agent.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()