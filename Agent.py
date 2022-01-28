import Game
import pygame
import random
import numpy as np
import Model
import sys

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
        self.epsilon = 0.2
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
        #   food location [south] ]
        self.state_size = 11
        # [right,   0
        #  left,    1
        #  fwd,     2
        self.actions = ['RIGHT', 'LEFT', 'FWD']
        self.action_size = len(self.actions)
        # compass
        self.compass = ['EAST', 'WEST', 'NORTH', 'SOUTH']
        self.compass_size = len(self.compass)
        # exit condition for an episode other than dying
        self.frame_iteration = 0
        self.max_iteration = 500
        # deep network
        self.model = Model.DQNModel(self.state_size, self.action_size)

        # init agent, then environment
        self.init_agent()
        self.env = Game.Environment(self.snake)

    # init agent
    def init_agent(self):
        # random heading
        self.direction = random.randrange(0, self.compass_size)
        self.head = Game.Point(Game.WIDTH / 2, Game.HEIGHT / 2)
        # random positioning
        x1, y1 = 0, 0
        if self.direction == self.compass.index('EAST'):
            x1 = self.head.x - Game.BLOCK_SIZE
            y1 = self.head.y
        elif self.direction == self.compass.index('WEST'):
            x1 = self.head.x + Game.BLOCK_SIZE
            y1 = self.head.y
        elif self.direction == self.compass.index('NORTH'):
            x1 = self.head.x
            y1 = self.head.y + Game.BLOCK_SIZE
        elif self.direction == self.compass.index('SOUTH'):
            x1 = self.head.x
            y1 = self.head.y - Game.BLOCK_SIZE

        self.snake = [self.head, Game.Point(x1, y1)]
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

        dir_e = self.direction == self.compass.index('EAST')
        dir_w = self.direction == self.compass.index('WEST')
        dir_n = self.direction == self.compass.index('NORTH')
        dir_s = self.direction == self.compass.index('SOUTH')

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
            self.env.food.y > head.y   # food is southbound
        ]
        return np.array(state, dtype=int)

    # get action using epsilon-greedy method to be taken from current
    # state
    def get_action(self, state):
        # exploration
        if random.uniform(0, 1) < self.epsilon:
            return 0, random.randrange(0, self.action_size)
        # exploitation; get action from pred_model and take the biggest
        # q value (best action)
        else:
            # reshape state array to feed into NN
            state = state.reshape(1, self.state_size)
            return 1, np.argmax(self.model.pred_model.predict(state))

    # step function takes in action, moves agent to next state and returns
    # [next_state, reward, done]
    def play_step(self, action):
        done = False
        self.score = 0
        self.frame_iteration += 1
        # Collect the user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.direction = self.get_new_direction(action)
        # move/change head (x, y)
        x = self.head.x
        y = self.head.y
        if self.direction == self.compass.index('EAST'):
            x += Game.BLOCK_SIZE
        elif self.direction == self.compass.index('WEST'):
            x -= Game.BLOCK_SIZE
        elif self.direction == self.compass.index('NORTH'):
            y -= Game.BLOCK_SIZE
        elif self.direction == self.compass.index('SOUTH'):
            y += Game.BLOCK_SIZE

        # update head (x, y)
        self.head = Game.Point(x, y)
        self.snake.insert(0, self.head)

        # Check if game over or exceeded set max iteration
        if self.env.is_collision():
            self.frame_iteration = 0
            done = True
            self.score = self.game_over_reward

        elif self.frame_iteration > self.max_iteration:
            print('frame iteration exceeded !')
            self.frame_iteration = 0
            done = True
            self.score = self.game_over_reward

        if not done:
            # Place new Food or just move
            if self.head == self.env.food:
                self.frame_iteration = 0
                self.score = self.food_reward
                self.env.place_food()
            # idle state
            else:
                self.snake.pop()

        # Update UI and clock
        self.env.update_ui(self.score)
        # get next state
        next_state = self.get_state()
        self.show_state(next_state)
        # update screen with debug info
        pygame.display.update()
        FramePerSec.tick(Game.SPEED)

        # Return game Over and Display Score
        return next_state, self.score, done

    def get_new_direction(self, action):
        new_direction = self.direction
        if self.direction == self.compass.index('EAST'):
            if action == self.actions.index('RIGHT'):
                new_direction = self.compass.index('SOUTH')
            elif action == self.actions.index('LEFT'):
                new_direction = self.compass.index('NORTH')

        elif self.direction == self.compass.index('WEST'):
            if action == self.actions.index('RIGHT'):
                new_direction = self.compass.index('NORTH')
            elif action == self.actions.index('LEFT'):
                new_direction = self.compass.index('SOUTH')

        elif self.direction == self.compass.index('NORTH'):
            if action == self.actions.index('RIGHT'):
                new_direction = self.compass.index('EAST')
            elif action == self.actions.index('LEFT'):
                new_direction = self.compass.index('WEST')

        elif self.direction == self.compass.index('SOUTH'):
            if action == self.actions.index('RIGHT'):
                new_direction = self.compass.index('WEST')
            elif action == self.actions.index('LEFT'):
                new_direction = self.compass.index('EAST')

        return new_direction

    # display state
    def show_state(self, state):
        # display state vector
        debugfont = pygame.font.SysFont("Verdana", 15)

        state_text = ["[R DNG] ", "[L DNG] ", "[F DNG] ",
                      "[E DIR] ", "[W DIR] ", "[N DIR] ", "[S DIR] ",
                      "[E FUD] ", "[W FUD] ", "[N FUD] ", "[S FUD] "]
        h = 0
        for i in range(len(state)):
            debugsurface = debugfont.render(state_text[i] + str(state[i]), True, Game.RED)
            Game.displaysurface.blit(debugsurface, (10, 10 + h))
            h += 20
        # debug info
        debugsurface = debugfont.render(str(self.frame_iteration), True, Game.YELLOW)
        Game.displaysurface.blit(debugsurface, (10, 10 + h))
        h += 20


def safe_close():
    pygame.quit()
    sys.exit()

