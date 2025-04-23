#include <SDL2/SDL.h>
#include <cmath>
#include <random>
#include <vector>
#include <stack>
#include <set>
#include <iostream>
#include <utility>
#include <algorithm>
#include <ctime>

// -----------------------------------------------------
// Global constants
// -----------------------------------------------------
static const int INITIAL_SCREEN_WIDTH  = 200;
static const int INITIAL_SCREEN_HEIGHT = 200;
static const int CELL_SIZE            = 40;
static const int WALL_THICKNESS       = 3;
static const double BOT_SPEED         = 1.0;
static const double MUTATION_RATE     = 0.1;
static const int NUMERO_BOTS          = 50;

// Robot & Sensor parameters
static const double DEFAULT_SENSOR_RANGE = 40.0;
static const int    DEFAULT_BOT_RADIUS   = 10;

// Angles in radians
static const double SENSOR_ANGLE_FRONTAL = 0.0;
static const double SENSOR_ANGLE_LEFT    = M_PI / 2.0;      // 90 degrees
static const double SENSOR_ANGLE_RIGHT   = -M_PI / 2.0;     // -90 degrees
static const double SENSOR_ANGLE_LEFT45  = M_PI / 4.0;      // 45 degrees
static const double SENSOR_ANGLE_RIGHT45 = -M_PI / 4.0;     // -45 degrees

// Energy parameters
static const double INITIAL_ENERGY   = 100.0;
static const double ENERGY_DECAY     = 0.1;   // lost each update
static const double ENERGY_RECOVERY  = 20.0;  // gained by eating food

// Food parameters
static const int    FOOD_RADIUS      = 5;
static const double FOOD_SPAWN_PROB  = 0.01;  // Probability of new food each frame

// -----------------------------------------------------
// Random utilities
// -----------------------------------------------------
static std::mt19937& rng() {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    return gen;
}

static double randDouble(double minVal, double maxVal) {
    std::uniform_real_distribution<double> dist(minVal, maxVal);
    return dist(rng());
}

static int randInt(int minVal, int maxVal) {
    std::uniform_int_distribution<int> dist(minVal, maxVal);
    return dist(rng());
}

// -----------------------------------------------------
// Cell class for Maze Generation
// -----------------------------------------------------
struct Cell {
    int i;  // column index
    int j;  // row index
    // Walls: [top, right, bottom, left]
    bool walls[4];
    bool visited;

    Cell(int col, int row) : i(col), j(row), visited(false) {
        walls[0] = walls[1] = walls[2] = walls[3] = true;
    }
};

// -----------------------------------------------------
// Maze class
// -----------------------------------------------------
class Maze {
public:
    Maze(int width, int height, int cellSize, int wallThickness)
        : m_width(width)
        , m_height(height)
        , m_cellSize(cellSize)
        , m_wallThickness(wallThickness)
    {
        m_cols = (m_width  / m_cellSize);
        m_rows = (m_height / m_cellSize);

        // Create the grid of cells
        for (int i = 0; i < m_cols; i++) {
            std::vector<Cell> column;
            column.reserve(m_rows);
            for (int j = 0; j < m_rows; j++) {
                column.emplace_back(i, j);
            }
            m_grid.push_back(column);
        }

        generateMaze();
        buildWalls();
        defineExit();
    }

    // Draw the maze walls and the exit rectangle
    void draw(SDL_Renderer* renderer) const {
        // Draw walls (in black)
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        for (auto& w : m_walls) {
            SDL_RenderFillRect(renderer, &w);
        }

        // Draw the exit area in green
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255);
        SDL_RenderFillRect(renderer, &m_exit);
    }

    // Returns true if the (x, y) point is within the exit rectangle
    bool isInExit(double x, double y) const {
        return (x >= m_exit.x && x <= (m_exit.x + m_exit.w) &&
                y >= m_exit.y && y <= (m_exit.y + m_exit.h));
    }

    // Accessors
    const std::vector<SDL_Rect>& getWalls() const { return m_walls; }
    const SDL_Rect& getExitRect() const { return m_exit; }
    int getWidth()  const { return m_width; }
    int getHeight() const { return m_height; }
    int getCellSize() const { return m_cellSize; }
    int getCols() const { return m_cols; }
    int getRows() const { return m_rows; }

private:
    int m_width;
    int m_height;
    int m_cellSize;
    int m_wallThickness;
    int m_cols;
    int m_rows;

    std::vector<std::vector<Cell>> m_grid; // grid[col][row]
    std::vector<SDL_Rect> m_walls;
    SDL_Rect m_exit;

    void generateMaze() {
        // Recursive backtracking
        std::stack<Cell*> stack;
        Cell* current = &m_grid[0][0];
        current->visited = true;
        stack.push(current);

        while (!stack.empty()) {
            current = stack.top();
            Cell* nextCell = checkNeighbors(*current);
            if (nextCell) {
                nextCell->visited = true;
                stack.push(nextCell);
                removeWalls(*current, *nextCell);
            } else {
                stack.pop();
            }
        }
    }

    Cell* checkNeighbors(const Cell& cell) {
        std::vector<Cell*> neighbors;
        neighbors.reserve(4);

        int i = cell.i;
        int j = cell.j;

        // Up
        if (j - 1 >= 0 && !m_grid[i][j - 1].visited) {
            neighbors.push_back(&m_grid[i][j - 1]);
        }
        // Right
        if (i + 1 < m_cols && !m_grid[i + 1][j].visited) {
            neighbors.push_back(&m_grid[i + 1][j]);
        }
        // Down
        if (j + 1 < m_rows && !m_grid[i][j + 1].visited) {
            neighbors.push_back(&m_grid[i][j + 1]);
        }
        // Left
        if (i - 1 >= 0 && !m_grid[i - 1][j].visited) {
            neighbors.push_back(&m_grid[i - 1][j]);
        }

        if (!neighbors.empty()) {
            int idx = randInt(0, (int)neighbors.size() - 1);
            return neighbors[idx];
        }
        return nullptr;
    }

    void removeWalls(Cell& current, Cell& nextCell) {
        int dx = nextCell.i - current.i;
        int dy = nextCell.j - current.j;

        if (dx == 1) {
            // next to the right
            current.walls[1] = false;  // current right
            nextCell.walls[3] = false; // next left
        } else if (dx == -1) {
            // next to the left
            current.walls[3] = false;  // current left
            nextCell.walls[1] = false; // next right
        } else if (dy == 1) {
            // next below
            current.walls[2] = false;  // current bottom
            nextCell.walls[0] = false; // next top
        } else if (dy == -1) {
            // next above
            current.walls[0] = false;  // current top
            nextCell.walls[2] = false; // next bottom
        }
    }

    void buildWalls() {
        m_walls.clear();
        for (int j = 0; j < m_rows; j++) {
            for (int i = 0; i < m_cols; i++) {
                int x = i * m_cellSize;
                int y = j * m_cellSize;
                const Cell& cell = m_grid[i][j];

                // top
                if (cell.walls[0]) {
                    SDL_Rect r { x, y, m_cellSize, m_wallThickness };
                    m_walls.push_back(r);
                }
                // right
                if (cell.walls[1]) {
                    SDL_Rect r { x + m_cellSize - m_wallThickness, y,
                                 m_wallThickness, m_cellSize };
                    m_walls.push_back(r);
                }
                // bottom
                if (cell.walls[2]) {
                    SDL_Rect r { x, y + m_cellSize - m_wallThickness,
                                 m_cellSize, m_wallThickness };
                    m_walls.push_back(r);
                }
                // left
                if (cell.walls[3]) {
                    SDL_Rect r { x, y, m_wallThickness, m_cellSize };
                    m_walls.push_back(r);
                }
            }
        }
    }

    void defineExit() {
        // Bottom-right cell interior
        int i = m_cols - 1;
        int j = m_rows - 1;
        int x = i * m_cellSize + m_wallThickness;
        int y = j * m_cellSize + m_wallThickness;

        m_exit.x = x;
        m_exit.y = y;
        m_exit.w = m_cellSize - 2 * m_wallThickness;
        m_exit.h = m_cellSize - 2 * m_wallThickness;
    }
};

// -----------------------------------------------------
// Bot (Robot) class
// -----------------------------------------------------
class Bot {
public:
    Bot(double x, double y, double angle,
        const std::vector<double>& sensorAngles = {},
        double sensorRange = DEFAULT_SENSOR_RANGE,
        int botRadius = DEFAULT_BOT_RADIUS,
        const std::vector<double>& sensorWeights = {},
        double bias = 0.0)
    {
        m_pos[0] = x;
        m_pos[1] = y;
        m_angle  = angle;

        if (sensorAngles.empty()) {
            m_sensorAngles = {
                SENSOR_ANGLE_FRONTAL,
                SENSOR_ANGLE_LEFT,
                SENSOR_ANGLE_RIGHT,
                SENSOR_ANGLE_LEFT45,
                SENSOR_ANGLE_RIGHT45
            };
        } else {
            m_sensorAngles = sensorAngles;
        }

        m_sensorRange = sensorRange;
        m_botRadius   = botRadius;

        if (sensorWeights.empty()) {
            for (size_t i = 0; i < m_sensorAngles.size(); i++) {
                m_sensorWeights.push_back(randDouble(-1.0, 1.0));
            }
        } else {
            m_sensorWeights = sensorWeights;
        }

        m_bias    = (bias == 0.0) ? randDouble(-0.1, 0.1) : bias;
        m_energy  = INITIAL_ENERGY;
        m_alive   = true;
        m_lifetime = 0.0;  // We'll count frames as a measure of time alive
    }

    void update(const Maze& maze, const std::vector<std::pair<double,double>>& foods) {
        if (!m_alive) return;

        // Increment lifetime (one frame)
        m_lifetime += 1.0;

        // Decay energy
        m_energy -= ENERGY_DECAY;
        if (m_energy <= 0.0) {
            m_alive = false;
            return;
        }

        // Gather sensor data
        std::vector<std::tuple<double, double, double>> sensorData; // (reading, absoluteAngle, offset)
        sensorData.reserve(m_sensorAngles.size());

        for (auto offset : m_sensorAngles) {
            double sensorAngle = m_angle + offset;
            double reading = getSensorReading(maze, sensorAngle, foods);
            sensorData.push_back({reading, sensorAngle, offset});
        }

        // Check if any sensor sees the exit strongly
        bool headingForExit     = false;
        double bestAngleForExit = 0.0;
        double bestExitReading  = 0.0;

        for (auto& sd : sensorData) {
            double r    = std::get<0>(sd);
            double sAng = std::get<1>(sd);
            // If exit reading is, say, 1.2 or higher
            if (r >= 1.2) {
                headingForExit = true;
                if (r > bestExitReading) {
                    bestExitReading  = r;
                    bestAngleForExit = sAng;
                }
            }
        }

        // If sensor sees the exit, steer towards it
        if (headingForExit) {
            m_angle = bestAngleForExit;
        }
        else {
            // Weighted steering
            double steering = m_bias;
            for (size_t i = 0; i < m_sensorWeights.size(); i++) {
                double reading = std::get<0>(sensorData[i]);
                steering += m_sensorWeights[i] * reading;
            }
            m_angle += (steering * 0.1);
        }

        // Compute new position
        double dx = BOT_SPEED * std::cos(m_angle);
        double dy = BOT_SPEED * std::sin(m_angle);

        double new_x = m_pos[0] + dx;
        double new_y = m_pos[1] + dy;

        // Check collisions with walls
        SDL_Rect botRect;
        botRect.x = (int)(new_x - m_botRadius);
        botRect.y = (int)(new_y - m_botRadius);
        botRect.w = m_botRadius * 2;
        botRect.h = m_botRadius * 2;

        bool collision = false;
        for (const auto& wall : maze.getWalls()) {
            if (SDL_HasIntersection(&botRect, &wall)) {
                collision = true;
                break;
            }
        }

        if (!collision) {
            m_pos[0] = new_x;
            m_pos[1] = new_y;
        } else {
            // Random angle adjustment if collision
            m_angle += randDouble(-0.5, 0.5);
        }
    }

    void draw(SDL_Renderer* renderer,
              const Maze& maze,
              const std::vector<std::pair<double,double>>& foods) const
    {
        // Bot as a blue circle
        SDL_SetRenderDrawColor(renderer, 0, 0, 255, 255);
        drawCircle(renderer, (int)m_pos[0], (int)m_pos[1], m_botRadius);

        // Sensors in green
        SDL_SetRenderDrawColor(renderer, 0, 255, 0, 255);
        for (auto offset : m_sensorAngles) {
            double sensorAngle = m_angle + offset;
            auto endPt = sensorEndpoint(maze, foods, sensorAngle);
            SDL_RenderDrawLine(renderer, (int)m_pos[0], (int)m_pos[1],
                               (int)endPt.first, (int)endPt.second);
        }

        // Energy ring (red) around the bot
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
        double ratio = m_energy / INITIAL_ENERGY;
        int radius   = (int)(m_botRadius * ratio);
        if (radius > 0) {
            drawCircle(renderer, (int)m_pos[0], (int)m_pos[1], radius, /*filled=*/false);
        }
    }

    bool isAlive() const { return m_alive; }

    // "Time alive" in frames
    double getLifetime() const { return m_lifetime; }

    // Current position
    std::pair<double, double> getPos() const {
        return {m_pos[0], m_pos[1]};
    }

    // Gain energy (by eating food)
    void addEnergy(double amount) {
        m_energy = std::min(m_energy + amount, INITIAL_ENERGY);
    }

    // Access for mutation
    const std::vector<double>& getSensorAngles() const { return m_sensorAngles; }
    double getSensorRange()  const { return m_sensorRange; }
    int    getBotRadius()    const { return m_botRadius; }
    const std::vector<double>& getSensorWeights() const { return m_sensorWeights; }
    double getBias()         const { return m_bias; }

    // For next generation
    void setPos(double x, double y) {
        m_pos[0] = x;
        m_pos[1] = y;
    }
    void reset() {
        m_energy    = INITIAL_ENERGY;
        m_alive     = true;
        m_lifetime  = 0.0;
    }

private:
    double m_pos[2]; 
    double m_angle;

    // Sensors
    std::vector<double> m_sensorAngles;
    double m_sensorRange;
    int    m_botRadius;

    // "Neural" weights
    std::vector<double> m_sensorWeights;
    double m_bias;

    // Energy + alive
    double m_energy;
    bool   m_alive;

    // New metric: number of frames stayed alive
    double m_lifetime;

    // -----------------------------------------------------
    // getSensorReading
    // -----------------------------------------------------
    double getSensorReading(const Maze& maze,
                            double sensorAngle,
                            const std::vector<std::pair<double,double>>& foods) const
    {
        const int step = 5;
        for (int dist = 0; dist <= (int)m_sensorRange; dist += step) {
            double test_x = m_pos[0] + dist * std::cos(sensorAngle);
            double test_y = m_pos[1] + dist * std::sin(sensorAngle);

            // 1) Check exit (priority)
            if (maze.isInExit(test_x, test_y)) {
                // Return something > 1.0 to indicate exit
                return 1.2;
            }

            // 2) Check food
            for (auto& f : foods) {
                double fx = f.first;
                double fy = f.second;
                double d2 = std::hypot(test_x - fx, test_y - fy);
                if (d2 <= FOOD_RADIUS) {
                    // Return something between 1.0 and exit
                    return 1.1;
                }
            }

            // 3) Check wall collision
            SDL_Rect testRect { (int)test_x, (int)test_y, 2, 2 };
            for (auto& w : maze.getWalls()) {
                if (SDL_HasIntersection(&testRect, &w)) {
                    return (m_sensorRange - dist) / m_sensorRange;
                }
            }
        }
        return 0.0;
    }

    // -----------------------------------------------------
    // sensorEndpoint
    // -----------------------------------------------------
    std::pair<double,double> sensorEndpoint(const Maze& maze,
                                            const std::vector<std::pair<double,double>>& foods,
                                            double sensorAngle) const
    {
        const int step = 5;
        for (int dist = 0; dist <= (int)m_sensorRange; dist += step) {
            double test_x = m_pos[0] + dist * std::cos(sensorAngle);
            double test_y = m_pos[1] + dist * std::sin(sensorAngle);

            // Check exit
            if (maze.isInExit(test_x, test_y)) {
                return {test_x, test_y};
            }
            // Check food
            for (auto& f : foods) {
                double fx = f.first;
                double fy = f.second;
                double d2 = std::hypot(test_x - fx, test_y - fy);
                if (d2 <= FOOD_RADIUS) {
                    return {test_x, test_y};
                }
            }
            // Check walls
            SDL_Rect testRect { (int)test_x, (int)test_y, 2, 2 };
            for (auto& w : maze.getWalls()) {
                if (SDL_HasIntersection(&testRect, &w)) {
                    return {test_x, test_y};
                }
            }
        }
        double end_x = m_pos[0] + m_sensorRange * std::cos(sensorAngle);
        double end_y = m_pos[1] + m_sensorRange * std::sin(sensorAngle);
        return {end_x, end_y};
    }

    // -----------------------------------------------------
    // Simple circle drawing
    // -----------------------------------------------------
    static void drawCircle(SDL_Renderer* renderer,
                           int centerX,
                           int centerY,
                           int radius,
                           bool filled = true)
    {
        if (filled) {
            for (int w = -radius; w <= radius; w++) {
                for (int h = -radius; h <= radius; h++) {
                    if (w*w + h*h <= radius*radius) {
                        SDL_RenderDrawPoint(renderer, centerX + w, centerY + h);
                    }
                }
            }
        } else {
            // perimeter only
            int x = radius;
            int y = 0;
            int err = 0;
            while (x >= y) {
                SDL_RenderDrawPoint(renderer, centerX + x, centerY + y);
                SDL_RenderDrawPoint(renderer, centerX + y, centerY + x);
                SDL_RenderDrawPoint(renderer, centerX - y, centerY + x);
                SDL_RenderDrawPoint(renderer, centerX - x, centerY + y);
                SDL_RenderDrawPoint(renderer, centerX - x, centerY - y);
                SDL_RenderDrawPoint(renderer, centerX - y, centerY - x);
                SDL_RenderDrawPoint(renderer, centerX + y, centerY - x);
                SDL_RenderDrawPoint(renderer, centerX + x, centerY - y);

                y += 1;
                if (err <= 0) {
                    err += 2*y + 1;
                }
                if (err > 0) {
                    x -= 1;
                    err -= 2*x + 1;
                }
            }
        }
    }
};

// -----------------------------------------------------
// Helper: Spawn food at a random cell center
// -----------------------------------------------------
std::pair<double,double> spawnFood(const Maze& maze) {
    int i = randInt(0, maze.getCols() - 1);
    int j = randInt(0, maze.getRows() - 1);
    double x = i * maze.getCellSize() + maze.getCellSize() / 2.0;
    double y = j * maze.getCellSize() + maze.getCellSize() / 2.0;
    return {x, y};
}

// -----------------------------------------------------
// Main
// -----------------------------------------------------
int main(int, char**) {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        std::cerr << "SDL could not initialize! SDL_Error: "
                  << SDL_GetError() << "\n";
        return 1;
    }

    int screenWidth  = INITIAL_SCREEN_WIDTH;
    int screenHeight = INITIAL_SCREEN_HEIGHT;

    SDL_Window* window = SDL_CreateWindow("Maze Bots",
                                          SDL_WINDOWPOS_CENTERED,
                                          SDL_WINDOWPOS_CENTERED,
                                          screenWidth,
                                          screenHeight,
                                          SDL_WINDOW_SHOWN);
    if (!window) {
        std::cerr << "Window could not be created! SDL_Error: "
                  << SDL_GetError() << "\n";
        SDL_Quit();
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window,
                                                -1,
                                                SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        std::cerr << "Renderer could not be created! SDL_Error: "
                  << SDL_GetError() << "\n";
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // Create the maze
    Maze maze(screenWidth, screenHeight, CELL_SIZE, WALL_THICKNESS);

    // Generation tracking
    int generation = 1;
    int numBots    = NUMERO_BOTS;

    // Start positions
    double startX = CELL_SIZE / 2.0;
    double startY = CELL_SIZE / 2.0;

    // Create initial bots
    std::vector<Bot> bots;
    bots.reserve(numBots);
    for (int i = 0; i < numBots; i++) {
        bots.emplace_back(startX, startY, 0.0);
    }

    bool running = true;
    std::vector<std::pair<double,double>> foods; // (x,y)

    Bot* winner = nullptr;

    // Track best candidate among ALL bots (alive or newly dead)
    Bot* bestCandidate = nullptr;
    double bestCandidateScore = 0.0;  // We'll track "time alive" as the score

    const int FPS = 60;
    const int frameDelay = 1000 / FPS;

    while (running) {
        Uint32 frameStart = SDL_GetTicks();
        SDL_Event event;

        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = false;
            }
        }

        // Possibly spawn new food
        if (randDouble(0.0, 1.0) < FOOD_SPAWN_PROB) {
            foods.push_back(spawnFood(maze));
        }

        // Clear background
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        SDL_RenderClear(renderer);

        // Draw maze
        maze.draw(renderer);

        // Draw food (red circles)
        SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255);
        for (auto& f : foods) {
            int fx = (int)f.first;
            int fy = (int)f.second;
            for (int w = -FOOD_RADIUS; w <= FOOD_RADIUS; w++) {
                for (int h = -FOOD_RADIUS; h <= FOOD_RADIUS; h++) {
                    if (w*w + h*h <= FOOD_RADIUS*FOOD_RADIUS) {
                        SDL_RenderDrawPoint(renderer, fx + w, fy + h);
                    }
                }
            }
        }

        // Update and draw bots
        winner = nullptr;
        for (auto& bot : bots) {
            if (bot.isAlive()) {
                bot.update(maze, foods);
                bot.draw(renderer, maze, foods);

                // Check if exit reached
                auto [bx, by] = bot.getPos();
                if (maze.isInExit(bx, by)) {
                    winner = &bot;
                }
            }

            // Whether alive or newly dead, see if it is the best candidate so far
            double botScore = bot.getLifetime();
            if (botScore > bestCandidateScore) {
                bestCandidateScore = botScore;
                bestCandidate = &bot;
            }
        }

        // Render the scene
        SDL_RenderPresent(renderer);

        // Bot<->food collision
        std::vector<std::pair<double,double>> remainingFoods;
        remainingFoods.reserve(foods.size());
        for (auto& f : foods) {
            bool eaten = false;
            for (auto& bot : bots) {
                if (bot.isAlive()) {
                    auto [bx, by] = bot.getPos();
                    double dist = std::hypot(bx - f.first, by - f.second);
                    if (dist < (bot.getBotRadius() + FOOD_RADIUS)) {
                        bot.addEnergy(ENERGY_RECOVERY);
                        eaten = true;
                        break;
                    }
                }
            }
            if (!eaten) {
                remainingFoods.push_back(f);
            }
        }
        foods = remainingFoods;

        // Remove dead bots from the vector
        bots.erase(std::remove_if(bots.begin(), bots.end(),
                                  [](const Bot& b){ return !b.isAlive(); }),
                   bots.end());

        // If we have a winner
        if (winner) {
            std::cout << "Winner found in generation " << generation << "!\n";

            // Use the winner's configuration to spawn next generation
            std::vector<Bot> newBots;
            newBots.reserve(numBots);

            for (int i = 0; i < numBots; i++) {
                // Mutate from winner
                std::vector<double> newSensorAngles = winner->getSensorAngles();
                for (auto& ang : newSensorAngles) {
                    ang += randDouble(-MUTATION_RATE, MUTATION_RATE);
                }

                double newSensorRange = winner->getSensorRange();
                newSensorRange += randDouble(-MUTATION_RATE*newSensorRange,
                                             MUTATION_RATE*newSensorRange);

                int newBotRadius = winner->getBotRadius();
                double radiusMut = randDouble(-MUTATION_RATE*newBotRadius,
                                              MUTATION_RATE*newBotRadius);
                newBotRadius = std::max(1, (int)(newBotRadius + radiusMut));

                std::vector<double> newSensorWeights = winner->getSensorWeights();
                for (auto& w : newSensorWeights) {
                    w += randDouble(-MUTATION_RATE, MUTATION_RATE);
                }

                double newBias = winner->getBias();
                newBias += randDouble(-MUTATION_RATE, MUTATION_RATE);

                Bot newBot(startX, startY, 0.0,
                           newSensorAngles, newSensorRange, newBotRadius,
                           newSensorWeights, newBias);
                newBots.push_back(newBot);
            }
            bots = std::move(newBots);

            // Optionally grow the maze
            if (generation % 1 == 0) {
                if (numBots > 0) {
                    numBots -= 1;
                }
                if (screenHeight < 1080) {
                    screenWidth  += 4;
                    screenHeight += 4;
                }
                SDL_SetWindowSize(window, screenWidth, screenHeight);
                maze = Maze(screenWidth, screenHeight, CELL_SIZE, WALL_THICKNESS);

                // Reset new bots
                for (auto& bot : bots) {
                    bot.setPos(startX, startY);
                    bot.reset(); 
                }
            }

            // Next generation
            generation++;
            foods.clear();

            // Reset bestCandidate for the new generation
            bestCandidate      = nullptr;
            bestCandidateScore = 0.0;
        }

        // If all bots are dead (no winner) -> mutate from bestCandidate
        if (bots.empty()) {
            std::cout << "All bots died in generation " << generation
                      << ". Using best candidate to spawn next generation...\n";

            std::vector<Bot> newBots;
            newBots.reserve(numBots);

            if (!bestCandidate) {
                // Safety fallback if no bestCandidate (shouldn't happen)
                std::cout << "No bestCandidate found; spawning default random bots.\n";
                for (int i = 0; i < numBots; i++) {
                    newBots.emplace_back(startX, startY, 0.0);
                }
            } else {
                // Replicate from bestCandidate
                for (int i = 0; i < numBots; i++) {
                    std::vector<double> newSensorAngles = bestCandidate->getSensorAngles();
                    for (auto& ang : newSensorAngles) {
                        ang += randDouble(-MUTATION_RATE, MUTATION_RATE);
                    }

                    double newSensorRange = bestCandidate->getSensorRange();
                    newSensorRange += randDouble(-MUTATION_RATE*newSensorRange,
                                                 MUTATION_RATE*newSensorRange);

                    int newBotRadius = bestCandidate->getBotRadius();
                    double radiusMut = randDouble(-MUTATION_RATE*newBotRadius,
                                                  MUTATION_RATE*newBotRadius);
                    newBotRadius = std::max(1, (int)(newBotRadius + radiusMut));

                    std::vector<double> newSensorWeights = bestCandidate->getSensorWeights();
                    for (auto& w : newSensorWeights) {
                        w += randDouble(-MUTATION_RATE, MUTATION_RATE);
                    }

                    double newBias = bestCandidate->getBias();
                    newBias += randDouble(-MUTATION_RATE, MUTATION_RATE);

                    Bot newBot(startX, startY, 0.0,
                               newSensorAngles, newSensorRange, newBotRadius,
                               newSensorWeights, newBias);
                    newBots.push_back(newBot);
                }
            }

            bots = std::move(newBots);

            // Next generation
            generation++;
            // Rebuild the Maze (if desired) and clear foods
            maze = Maze(screenWidth, screenHeight, CELL_SIZE, WALL_THICKNESS);
            foods.clear();

            // Reset bestCandidate
            bestCandidate      = nullptr;
            bestCandidateScore = 0.0;
        }

        // Frame limiting
        Uint32 frameTime = SDL_GetTicks() - frameStart;
        if (frameDelay > frameTime) {
            SDL_Delay(frameDelay - frameTime);
        }
    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}

