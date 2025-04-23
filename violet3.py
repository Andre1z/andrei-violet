import random
import math

# ----------------------------- Maze Generation -----------------------------
class Maze:
    """
    Generates a random maze using a depth-first search "carving" approach.
    We'll store True = wall, False = open path.
    """
    def __init__(self, rows=10, cols=15):
        self.rows = rows
        self.cols = cols
        # Initialize a grid full of walls
        self.maze = [[True for _ in range(cols)] for _ in range(rows)]
        self.generate_maze()

    def generate_maze(self):
        stack = []
        # pick a random starting cell
        start_r = random.randint(0, self.rows - 1)
        start_c = random.randint(0, self.cols - 1)
        self.maze[start_r][start_c] = False  # carve it open
        stack.append((start_r, start_c))

        # relative moves for carving 2 steps at a time (to ensure walls remain)
        neighbors = [(-2, 0), (2, 0), (0, 2), (0, -2)]
        while stack:
            r, c = stack[-1]
            possible = []
            random.shuffle(neighbors)
            for dr, dc in neighbors:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.maze[nr][nc]:
                        # check the cell in between
                        mr, mc = r + dr // 2, c + dc // 2
                        if self.maze[mr][mc]:
                            possible.append((nr, nc, mr, mc))
            if possible:
                nr, nc, mr, mc = random.choice(possible)
                # carve the corridor
                self.maze[mr][mc] = False
                self.maze[nr][nc] = False
                stack.append((nr, nc))
            else:
                stack.pop()

    def is_wall(self, row, col):
        # Out-of-bounds is treated as wall
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return True
        return self.maze[row][col]

# -------------------- Tiny Neural Network for Q-Learning --------------------
class TinyNeuralNetwork:
    """
    A minimal multi-layer perceptron with one hidden layer.
    - Input size = 4 (which directions are open?).
    - Output size = 4 (Q-values for up/right/down/left).
    """
    def __init__(self, input_size=4, hidden_size=8, output_size=4, lr=0.01, gamma=0.95):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lr = lr       # learning rate
        self.gamma = gamma # discount factor

        # Initialize weights
        def rand_matrix(n_in, n_out):
            return [[random.uniform(-1.0/math.sqrt(n_in), 1.0/math.sqrt(n_in))
                     for _ in range(n_out)] for _ in range(n_in)]
        def rand_bias(n):
            return [0.0 for _ in range(n)]

        # input -> hidden
        self.W1 = rand_matrix(self.input_size, self.hidden_size)
        self.b1 = rand_bias(self.hidden_size)

        # hidden -> output
        self.W2 = rand_matrix(self.hidden_size, self.output_size)
        self.b2 = rand_bias(self.output_size)

        # Temporary values for forward pass
        self.z1 = [0.0]*self.hidden_size
        self.a1 = [0.0]*self.hidden_size
        self.z2 = [0.0]*self.output_size
        self.a2 = [0.0]*self.output_size

    def _relu(self, x):
        return max(0.0, x)

    def _relu_deriv(self, x):
        return 1.0 if x > 0 else 0.0

    def forward(self, inputs):
        """
        inputs: list of length 4
        returns: list of length 4 (the Q-values)
        """
        # Hidden layer
        for j in range(self.hidden_size):
            s = sum(inputs[i] * self.W1[i][j] for i in range(self.input_size))
            s += self.b1[j]
            self.z1[j] = s
            self.a1[j] = self._relu(s)

        # Output layer
        for k in range(self.output_size):
            s = sum(self.a1[j] * self.W2[j][k] for j in range(self.hidden_size))
            s += self.b2[k]
            # We'll keep the output linear
            self.z2[k] = s
            self.a2[k] = s

        return self.a2

    def backward(self, inputs, target, action_taken):
        """
        Adjust weights so that Q(s, a_taken) moves closer to 'target'.
        """
        # 1. Forward pass
        self.forward(inputs)

        # 2. Compute output deltas
        d_output = [0.0]*self.output_size
        error = target - self.a2[action_taken]
        d_output[action_taken] = error

        # 3. Grad for W2, b2
        dW2 = [[0.0]*self.output_size for _ in range(self.hidden_size)]
        db2 = [0.0]*self.output_size
        for k in range(self.output_size):
            db2[k] = d_output[k]
            for j in range(self.hidden_size):
                dW2[j][k] = d_output[k] * self.a1[j]

        # 4. Backprop to hidden
        d_hidden = [0.0]*self.hidden_size
        for j in range(self.hidden_size):
            downstream_sum = 0.0
            for k in range(self.output_size):
                downstream_sum += self.W2[j][k] * d_output[k]
            d_hidden[j] = downstream_sum * self._relu_deriv(self.z1[j])

        # 5. Grad for W1, b1
        dW1 = [[0.0]*self.hidden_size for _ in range(self.input_size)]
        db1 = [0.0]*self.hidden_size
        for j in range(self.hidden_size):
            db1[j] = d_hidden[j]
            for i in range(self.input_size):
                dW1[i][j] = d_hidden[j] * inputs[i]

        # 6. Gradient descent update
        # hidden->output
        for j in range(self.hidden_size):
            for k in range(self.output_size):
                self.W2[j][k] += self.lr * dW2[j][k]
        for k in range(self.output_size):
            self.b2[k] += self.lr * db2[k]

        # input->hidden
        for i in range(self.input_size):
            for j in range(self.hidden_size):
                self.W1[i][j] += self.lr * dW1[i][j]
        for j in range(self.hidden_size):
            self.b1[j] += self.lr * db1[j]

# --------------------------- Mouse Agent ---------------------------
class MouseAgent:
    """
    The agent that moves in the maze, using a neural network to approximate Q-values.
    Observations: whether up/right/down/left are open (4 binary features).
    Actions: 0=up, 1=right, 2=down, 3=left.
    """
    def __init__(self, maze, neural_net, start_r=0, start_c=0, epsilon=0.2, gamma=0.95):
        self.maze = maze
        self.net = neural_net
        self.epsilon = epsilon
        self.gamma = gamma
        self.reset(start_r, start_c)

    def reset(self, start_r=0, start_c=0):
        self.row = start_r
        self.col = start_c
        self.visited = set()
        self.visited.add((self.row, self.col))

    def get_state(self):
        """
        Return a 4-length list [open_up, open_right, open_down, open_left].
          - 1.0 if open
          - 0.0 if wall
        """
        up    = 0.0 if self.maze.is_wall(self.row - 1, self.col) else 1.0
        right = 0.0 if self.maze.is_wall(self.row, self.col + 1) else 1.0
        down  = 0.0 if self.maze.is_wall(self.row + 1, self.col) else 1.0
        left  = 0.0 if self.maze.is_wall(self.row, self.col - 1) else 1.0
        return [up, right, down, left]

    def choose_action(self, state):
        """
        Epsilon-greedy strategy. Return action in {0,1,2,3}.
        """
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        else:
            q_vals = self.net.forward(state)
            return max(range(4), key=lambda i: q_vals[i])

    def step(self):
        """
        Perform one step in the environment:
          - Choose an action
          - Move (if not blocked by wall)
          - Receive reward
          - Update Q-values
        Returns (done, reward):
          - done: True if we reached the goal
          - reward: the immediate reward received
        """
        s = self.get_state()
        a = self.choose_action(s)

        # intended next position
        nr, nc = self.row, self.col
        if a == 0:  # up
            nr -= 1
        elif a == 1:  # right
            nc += 1
        elif a == 2:  # down
            nr += 1
        else:  # left
            nc -= 1

        # reward shaping
        reward = 0.0
        if self.maze.is_wall(nr, nc):
            # bump into wall
            reward = -1.0
            nr, nc = self.row, self.col  # remain in place
        else:
            # valid move
            self.row, self.col = nr, nc
            if (nr, nc) in self.visited:
                # penalty for revisiting
                reward = -1.0
            self.visited.add((nr, nc))

        # check if we reached the goal: bottom-right cell
        if (self.row == self.maze.rows - 1) and (self.col == self.maze.cols - 1):
            reward = 10.0
            done = True
        else:
            done = False

        # Q-learning update
        s_next = self.get_state()
        q_next = self.net.forward(s_next)
        best_next = max(q_next)
        target = reward + self.gamma * best_next
        self.net.backward(s, target, a)

        return done, reward

# --------------------------- Main Training Loop ---------------------------
def run_training(num_episodes=1000, max_steps_per_episode=200,
                 maze_rows=10, maze_cols=15,
                 print_interval=50):
    """
    Train the mouse agent in a random maze for a specified number of episodes.
    """
    # 1) Create the random maze
    maze = Maze(rows=maze_rows, cols=maze_cols)

    # 2) Create the neural network
    net = TinyNeuralNetwork(input_size=4, hidden_size=8, output_size=4, lr=0.01, gamma=0.95)

    # 3) Create the agent
    agent = MouseAgent(maze, net, start_r=0, start_c=0, epsilon=0.2, gamma=0.95)

    # For logging
    episode_rewards = []
    episode_goal_reached = 0

    for episode in range(1, num_episodes+1):
        agent.reset(0, 0)  # start top-left
        total_reward = 0.0
        done = False
        steps = 0

        for _ in range(max_steps_per_episode):
            steps += 1
            done, reward = agent.step()
            total_reward += reward
            if done:
                break

        # Logging
        episode_rewards.append(total_reward)
        if done:
            episode_goal_reached += 1

        if episode % print_interval == 0:
            avg_reward = sum(episode_rewards[-print_interval:]) / print_interval
            print(f"Episode {episode}/{num_episodes}: "
                  f"Steps={steps}, Reward={total_reward:.2f}, "
                  f"ReachedGoal={'Yes' if done else 'No'}, "
                  f"AvgReward(Last{print_interval})={avg_reward:.2f}")

    # Final stats
    overall_avg_reward = sum(episode_rewards) / num_episodes
    print("\nTraining completed.")
    print(f"  Episodes: {num_episodes}")
    print(f"  Maze size: {maze_rows}x{maze_cols}")
    print(f"  Goal Reached in {episode_goal_reached} out of {num_episodes} episodes.")
    print(f"  Overall Average Reward: {overall_avg_reward:.2f}")

# --------------------------- Main Execution ---------------------------
if __name__ == "__main__":
    # You can adjust the hyperparameters here as you wish:
    run_training(
        num_episodes=500,
        max_steps_per_episode=200,
        maze_rows=10,
        maze_cols=15,
        print_interval=50
    )
