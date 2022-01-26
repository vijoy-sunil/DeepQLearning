import Game
import pygame
import random
import numpy as np
import Model
import sys
import math

FramePerSec = pygame.time.Clock()

class Agent:
    def __init__(self):
        # agent variables
        self.score = 0
        self.snake = None
        self.head = None
        self.direction = None
        # reward collected by agent
        self.game_over_reward = -5
        self.food_reward = 10
        # constants
        self.epsilon = 0.8
        # [ next block [right] danger,
        #   next block [left]  danger,
        #   next block [fwd]   danger,
        #   face direction [east],
        #   face direction [west],
        #   face direction [north],
        #   face direction [south],
        #   food location [east],
        #   food location [west],
        #   food location [north],
        #   food location [south],
        #   distance to food ]
        self.state_size = 12
        # [east,       0
        #  west,       1
        #  north,      2
        #  south]      3
        self.actions = ['EAST', 'WEST', 'NORTH', 'SOUTH']
        self.action_size = len(self.actions)
        # exit condition for an episode other than dying
        self.frame_iteration = 0
        self.max_iteration = 500
        # deep network
        self.model = Model.DQNModel()

        # init agent, then environment
        self.init_agent()
        self.env = Game.Environment(self.snake)

    # init agent
    def init_agent(self):
        self.direction = self.actions.index('EAST')
        self.head = Game.Point(Game.WIDTH / 2, Game.HEIGHT / 2)
        self.snake = [self.head,
                      Game.Point(self.head.x - Game.BLOCK_SIZE, self.head.y),
                      Game.Point(self.head.x - (2 * Game.BLOCK_SIZE), self.head.y)]
        self.score = 0

    # reset
    def safe_reset(self):
        self.init_agent()
        self.env.init_env(self.snake)
        self.env.update_ui(self.score)
        pygame.display.update()

    # get current state
    def get_state(self):
        head = self.snake[0]
        # neighboring cells
        point_r = Game.Point(head.x + Game.BLOCK_SIZE, head.y)
        point_l = Game.Point(head.x - Game.BLOCK_SIZE, head.y)
        point_u = Game.Point(head.x, head.y - Game.BLOCK_SIZE)
        point_d = Game.Point(head.x, head.y + Game.BLOCK_SIZE)

        dir_e = self.direction == self.actions.index('EAST')
        dir_w = self.direction == self.actions.index('WEST')
        dir_n = self.direction == self.actions.index('NORTH')
        dir_s = self.direction == self.actions.index('SOUTH')

        # metric
        distance_to_food = math.dist(head, self.env.food)
        # construct state vector
        state = [
            # next block [right]  danger
            (dir_e and self.env.is_collision(point_d)) or
            (dir_w and self.env.is_collision(point_u)) or
            (dir_n and self.env.is_collision(point_r)) or
            (dir_s and self.env.is_collision(point_l)),

            # next block [left]  danger
            (dir_e and self.env.is_collision(point_u)) or
            (dir_w and self.env.is_collision(point_d)) or
            (dir_n and self.env.is_collision(point_l)) or
            (dir_s and self.env.is_collision(point_r)),

            # next block [fwd] danger
            (dir_e and self.env.is_collision(point_r)) or
            (dir_w and self.env.is_collision(point_l)) or
            (dir_n and self.env.is_collision(point_u)) or
            (dir_s and self.env.is_collision(point_d)),

            # face direction
            dir_e,
            dir_w,
            dir_n,
            dir_s,

            # food location
            self.env.food.x > head.x,  # food is eastbound
            self.env.food.x < head.x,  # food is westbound
            self.env.food.y < head.y,  # food is northbound
            self.env.food.y > head.y,  # food is southbound

            distance_to_food            # distance to food
        ]
        return np.array(state, dtype=int)

    # get action using epsilon-greedy method to be taken from current
    # state
    def get_action(self, state):
        # exploration
        if random.uniform(0, 1) > self.epsilon:
            return random.randrange(0, self.action_size)
        # exploitation; get action from pred_model and take the biggest
        # q value (best action)
        else:
            # reshape state array to feed into NN
            state = state.reshape(1, self.state_size)
            return np.argmax(self.model.pred_model.predict(state))

    # step function takes in action, moves agent to next state and returns
    # [next_state, reward, done]
    def play_step(self, action):
        done = False
        self.frame_iteration += 1
        # Collect the user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # move/change head (x, y)
        x = self.head.x
        y = self.head.y
        if action == self.actions.index('EAST'):
            x += Game.BLOCK_SIZE
        elif action == self.actions.index('WEST'):
            x -= Game.BLOCK_SIZE
        elif action == self.actions.index('NORTH'):
            y -= Game.BLOCK_SIZE
        elif action == self.actions.index('SOUTH'):
            y += Game.BLOCK_SIZE

        self.direction = action
        # update head (x, y)
        self.head = Game.Point(x, y)
        self.snake.insert(0, self.head)

        # Check if game over or exceeded set max iteration
        if self.env.is_collision():
            done = True
            self.score += self.game_over_reward

        elif self.frame_iteration > self.max_iteration:
            self.frame_iteration = 0
            print('frame iteration exceeded !')
            done = True
            self.score += self.game_over_reward

        if not done:
            # Place new Food or just move
            if self.head == self.env.food:
                self.score += self.food_reward
                self.env.place_food()
            else:
                self.snake.pop()

        # Update UI and clock
        self.env.update_ui(self.score)
        # get next state
        next_state = self.get_state()
        show_state(next_state)
        # update screen with debug info
        pygame.display.update()
        FramePerSec.tick(Game.SPEED)

        # Return game Over and Display Score
        return next_state, self.score, done

# display state
def show_state(state):
    # display state vector
    debugfont = pygame.font.SysFont("Verdana", 14)
    h = 0
    for i in range(len(state)):
        debugsurface = debugfont.render(str(state[i]), True, Game.RED)
        Game.displaysurface.blit(debugsurface, (10, 30 + h))
        h += 20

def safe_close():
    pygame.quit()
    sys.exit()

