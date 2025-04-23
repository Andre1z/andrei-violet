import pygame
import random
import math
import sys

# -------------- Neural Network (Tiny MLP) --------------
class TinyNeuralNetwork:
    """
    A very simple multi-layer perceptron with one hidden layer.
    Designed for 4 inputs (observation of free/blocked in four directions)
    and 4 outputs (Q-values for up/right/down/left).
    """

    def __init__(self, input_size=4, hidden_size=8, output_size=4, lr=0.01, gamma=0.95):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lr = lr          # learning rate
        self.gamma = gamma    # discount factor

        # Initialize weights (Xavier-ish random)
        def rand_val(n_in, n_out):
            return [[random.uniform(-1.0/math.sqrt(n_in), 1.0/math.sqrt(n_in))
                     for _ in range(n_out)] for _ in range(n_in)]
        def rand_bias(n):
            return [0.0 for _ in range(n)]

        # We’ll have:
        #   input -> hidden
        #   hidden -> output
        self.W1 = rand_val(self.input_size, self.hidden_size)
        self.b1 = rand_bias(self.hidden_size)
        self.W2 = rand_val(self.hidden_size, self.output_size)
        self.b2 = rand_bias(self.output_size)

        # For storing forward pass results to use in backprop
        self.z1 = [0.0]*self.hidden_size
        self.a1 = [0.0]*self.hidden_size
        self.z2 = [0.0]*self.output_size
        self.a2 = [0.0]*self.output_size  # final output (the Q-values)

    def _relu(self, x):
        return max(0.0, x)

    def _relu_deriv(self, x):
        return 1.0 if x > 0 else 0.0

    def forward(self, inputs):
        """
        inputs: list of length input_size
        returns: list of length output_size (the Q-values)
        """
        # Hidden layer
        for j in range(self.hidden_size):
            self.z1[j] = sum(inputs[i]*self.W1[i][j] for i in range(self.input_size)) + self.b1[j]
            self.a1[j] = self._relu(self.z1[j])

        # Output layer
        for k in range(self.output_size):
            self.z2[k] = sum(self.a1[j]*self.W2[j][k] for j in range(self.hidden_size)) + self.b2[k]
            self.a2[k] = self.z2[k]  # (linear) or could do ReLU as well
        return self.a2

    def backward(self, inputs, target, action_taken):
        """
        Backprop to update weights given:
         - inputs:  current state (4 dims)
         - target:  the Q-target (scalar)
         - action_taken: which action index (0..3) was taken
        We only adjust Q(s,a_taken) to move closer to target.
        """

        # 1. Forward pass to get the current Q-values and save them
        self.forward(inputs)

        # 2. Output layer deltas
        # We only adjust the gradient for the action that was taken:
        d_output = [0.0]*self.output_size
        # error = (target - Q(s, a_taken))
        error = target - self.a2[action_taken]
        d_output[action_taken] = error  # derivative wrt the linear output

        # 3. Backprop from output to hidden
        # dW2, db2
        dW2 = [[0.0]*self.output_size for _ in range(self.hidden_size)]
        db2 = [0.0]*self.output_size
        for k in range(self.output_size):
            db2[k] = d_output[k]
            for j in range(self.hidden_size):
                dW2[j][k] = d_output[k] * self.a1[j]

        # 4. Hidden layer deltas
        d_hidden = [0.0]*self.hidden_size
        for j in range(self.hidden_size):
            # sum over output neurons
            sum_downstream = sum(self.W2[j][k]*d_output[k] for k in range(self.output_size))
            d_hidden[j] = sum_downstream * self._relu_deriv(self.z1[j])

        # 5. Backprop from hidden to input
        dW1 = [[0.0]*self.hidden_size for _ in range(self.input_size)]
        db1 = [0.0]*self.hidden_size
        for j in range(self.hidden_size):
            db1[j] = d_hidden[j]
            for i in range(self.input_size):
                dW1[i][j] = d_hidden[j] * inputs[i]

        # 6. Gradient descent update
        # Output layer
        for j in range(self.hidden_size):
            for k in range(self.output_size):
                self.W2[j][k] += self.lr * dW2[j][k]
        for k in range(self.output_size):
            self.b2[k] += self.lr * db2[k]

        # Hidden layer
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.W1[i][j] += self.lr * dW1[i][j]
        for j in range(self.hidden_size):
            self.b1[j] += self.lr * db1[j]


# -------------- Maze Generation (DFS) --------------
class Maze:
    """
    Generates a random maze using a Depth-First Search algorithm.
    `maze[w][h] = True` if that cell is a wall, False if open.
    """

    def __init__(self, rows=15, cols=20):
        self.rows = rows
        self.cols = cols
        # Start with a grid full of walls (True = wall)
        self.maze = [[True for _ in range(cols)] for _ in range(rows)]
        self.generate_maze()

    def generate_maze(self):
        # Carve out a random maze using DFS
        # We'll define a small utility stack-based DFS
        stack = []
        # pick a random starting cell
        start_r = random.randint(0, self.rows - 1)
        start_c = random.randint(0, self.cols - 1)
        self.maze[start_r][start_c] = False  # carve it (open)
        stack.append((start_r, start_c))

        neighbors = [(-2, 0), (2, 0), (0, 2), (0, -2)]
        while stack:
            r, c = stack[-1]
            # find all possible neighbors that can be carved
            possible = []
            random.shuffle(neighbors)
            for dr, dc in neighbors:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.maze[nr][nc]:  # if it's still a wall
                        # check the cell in between
                        mr, mc = r + dr // 2, c + dc // 2
                        if self.maze[mr][mc]:
                            possible.append((nr, nc, mr, mc))
            if possible:
                nr, nc, mr, mc = random.choice(possible)
                # carve the passage
                self.maze[mr][mc] = False
                self.maze[nr][nc] = False
                stack.append((nr, nc))
            else:
                stack.pop()

    def is_wall(self, row, col):
        # If out-of-bounds, treat it as a wall
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return True
        return self.maze[row][col]


# -------------- Agent (Mouse) --------------
class MouseAgent:
    """
    A simple agent that moves in the maze, uses a neural network to learn.
    """

    def __init__(self, maze, neural_net, start_r=0, start_c=0):
        self.maze = maze
        self.net = neural_net
        self.reset(start_r, start_c)
        self.epsilon = 0.2   # exploration rate
        self.gamma = 0.95    # discount factor

    def reset(self, start_r=0, start_c=0):
        self.row = start_r
        self.col = start_c
        self.visited = set()
        self.visited.add((self.row, self.col))

    def get_state(self):
        """
        Return a 4-dim state vector:
          [open_up, open_right, open_down, open_left]
        Each is 1.0 if open (not a wall), 0.0 if wall.
        """
        up    = 0.0 if self.maze.is_wall(self.row - 1, self.col) else 1.0
        right = 0.0 if self.maze.is_wall(self.row, self.col + 1) else 1.0
        down  = 0.0 if self.maze.is_wall(self.row + 1, self.col) else 1.0
        left  = 0.0 if self.maze.is_wall(self.row, self.col - 1) else 1.0
        return [up, right, down, left]

    def choose_action(self, state):
        """
        Epsilon-greedy choice: with probability epsilon pick random action,
        otherwise pick the best from the neural net Q-values.
        Action order: 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
        """
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        else:
            q_vals = self.net.forward(state)  # Q(s, :)
            # pick action with highest Q
            return max(range(4), key=lambda i: q_vals[i])

    def step(self):
        """
        Do one movement step in the maze, update the neural net.
        Returns True if we reached the goal (bottom-right).
        """
        state = self.get_state()
        action = self.choose_action(state)

        # figure out the intended next row/col
        if action == 0:  # up
            nr, nc = self.row - 1, self.col
        elif action == 1:  # right
            nr, nc = self.row, self.col + 1
        elif action == 2:  # down
            nr, nc = self.row + 1, self.col
        else:  # left
            nr, nc = self.row, self.col - 1

        # reward shaping
        reward = 0.0
        if self.maze.is_wall(nr, nc):
            # bump into wall
            reward = -1.0
            # agent doesn't move
            nr, nc = self.row, self.col
        else:
            # move
            self.row, self.col = nr, nc
            if (nr, nc) in self.visited:
                # penalty for revisiting same cell
                reward = -1.0
            self.visited.add((nr, nc))

        # check if we reached the goal (bottom-right)
        if self.row == self.maze.rows-1 and self.col == self.maze.cols-1:
            reward = 10.0

        # get next state, for learning update
        next_state = self.get_state()
        # Q-learning target for Q(s, a)
        q_next = self.net.forward(next_state)
        best_next = max(q_next)
        target = reward + self.gamma * best_next

        # update the network
        self.net.backward(state, target, action)

        # If the agent hits the goal, return True
        return (self.row == self.maze.rows-1 and self.col == self.maze.cols-1)


# -------------- Pygame Visualization --------------
def main():
    pygame.init()
    # window size in pixels
    CELL_SIZE = 30
    rows, cols = 15, 20
    width = cols * CELL_SIZE
    height = rows * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Random Maze with Mouse Agent")

    clock = pygame.time.Clock()

    # Create Maze
    maze = Maze(rows, cols)

    # Create a simple neural net
    net = TinyNeuralNetwork()

    # Create agent
    mouse = MouseAgent(maze, net, start_r=0, start_c=0)

    # Colors (R,G,B)
    WALL_COLOR   = (40, 40, 40)
    FLOOR_COLOR  = (200, 200, 200)
    MOUSE_COLOR  = (0, 0, 255)
    GOAL_COLOR   = (255, 165, 0)

    running = True

    while running:
        clock.tick(30)  # 30 frames per second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Let the mouse take one step per frame (learning in real time)
        reached_goal = mouse.step()
        if reached_goal:
            # When the goal is reached, reset the maze or the agent
            # to watch more learning episodes (optional).
            mouse.reset(0, 0)

        # ---------- Draw Maze ----------
        screen.fill((0, 0, 0))
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if maze.is_wall(r, c):
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                else:
                    pygame.draw.rect(screen, FLOOR_COLOR, rect)
        # Draw goal cell
        goal_rect = pygame.Rect((cols-1)*CELL_SIZE, (rows-1)*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GOAL_COLOR, goal_rect)

        # ---------- Draw Mouse ----------
        mx = mouse.col * CELL_SIZE + CELL_SIZE//2
        my = mouse.row * CELL_SIZE + CELL_SIZE//2
        pygame.draw.circle(screen, MOUSE_COLOR, (mx, my), CELL_SIZE//3)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
