import pygame
import sys
import random
import math

# Constants for window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Visual constants
NEURON_RADIUS = 10
CONNECTION_WIDTH = 2
BACKGROUND_COLOR = (0, 0, 0)       # Black
NEURON_COLOR = (255, 255, 255)     # White
EXCITED_COLOR = (255, 0, 0)        # Red
CONNECTION_COLOR = (0, 255, 0)     # Green

class Neurona:
    def __init__(self, x, y, neuron_id):
        """
        :param x: X-coordinate of the neuron
        :param y: Y-coordinate of the neuron
        :param neuron_id: A unique ID to identify this neuron
        """
        self.x = x
        self.y = y
        self.neuron_id = neuron_id
        self.connections = []  # Will store references to other Neurona objects
        self.is_excited = False

    def draw(self, screen):
        """
        Draw this neuron as a circle. If it’s excited, color it differently.
        """
        color = EXCITED_COLOR if self.is_excited else NEURON_COLOR
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), NEURON_RADIUS)

        # Draw connections
        for conn in self.connections:
            pygame.draw.line(
                screen,
                CONNECTION_COLOR,
                (self.x, self.y),
                (conn.x, conn.y),
                CONNECTION_WIDTH
            )

    def excite(self):
        """
        Make this neuron excited. Could trigger logic to form new connections.
        """
        self.is_excited = True

    def calm_down(self):
        """
        Example of how you might have a neuron calm down eventually.
        """
        self.is_excited = False

    def form_connection(self, other_neuron):
        """
        Create a connection (bond) between this neuron and another.
        Ensure we don't have duplicates.
        """
        if other_neuron not in self.connections and other_neuron != self:
            self.connections.append(other_neuron)
            # Also add the reverse connection in the other neuron
            other_neuron.connections.append(self)

    def distance_to(self, other_neuron):
        return math.hypot(self.x - other_neuron.x, self.y - other_neuron.y)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Neural Network Visualization")

    clock = pygame.time.Clock()

    # Create a list of neurons at random positions
    num_neurons = 20
    neurons = []
    for i in range(num_neurons):
        x = random.randint(50, WINDOW_WIDTH - 50)
        y = random.randint(50, WINDOW_HEIGHT - 50)
        neuron = Neurona(x, y, i)
        neurons.append(neuron)

    # Some parameters for our simple "network behavior"
    # maximum distance to form a bond
    CONNECTION_THRESHOLD = 100

    running = True
    while running:
        clock.tick(60)  # Frame rate of 60 FPS
        screen.fill(BACKGROUND_COLOR)

        # Process user input / events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Example stimulus input: press SPACE to excite random neuron(s)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Stimulate 1 random neuron
                    random_neuron = random.choice(neurons)
                    random_neuron.excite()

        # Update network logic
        for neuron in neurons:
            # If a neuron is excited, it can form new connections
            if neuron.is_excited:
                # Attempt to form connections with nearby neurons
                for other in neurons:
                    if other != neuron:
                        dist = neuron.distance_to(other)
                        if dist < CONNECTION_THRESHOLD:
                            neuron.form_connection(other)

                # Optionally, calm down the neuron after forming connections
                # so it's a one-time event. If you want them to remain excited, remove this.
                neuron.calm_down()

        # Draw neurons (and connections)
        for neuron in neurons:
            neuron.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
