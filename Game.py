import pygame
import random
from collections import namedtuple

# init pygame
pygame.init()

# Game params
WIDTH = 640
HEIGHT = 480
# powers of 20
BLOCK_SIZE = 40
SPEED = 16

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake DQN')
Point = namedtuple('Point', 'x , y')

class Environment:
    def __init__(self, player):
        self.w = WIDTH
        self.h = HEIGHT
        # variables
        self.snake = None
        self.food = None
        # init env
        self.init_env(player)

    def init_env(self, player):
        # get a copy of snake and then place food
        self.snake = player
        self.place_food()

    def place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        # retry placing food
        if self.food in self.snake:
            self.place_food()

    def update_ui(self, score):
        displaysurface.fill(BLACK)
        # different color for the head
        head = self.snake[0]
        for pt in self.snake:
            pygame.draw.rect(displaysurface, BLUE1,
                             pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            if pt == head:
                pygame.draw.rect(displaysurface, YELLOW,
                                 pygame.Rect(pt.x + 0.2 * BLOCK_SIZE, pt.y + 0.2 * BLOCK_SIZE,
                                             0.6 * BLOCK_SIZE, 0.6 * BLOCK_SIZE))
            else:
                pygame.draw.rect(displaysurface, BLUE2,
                                 pygame.Rect(pt.x + 0.2 * BLOCK_SIZE, pt.y + 0.2 * BLOCK_SIZE,
                                             0.6 * BLOCK_SIZE, 0.6 * BLOCK_SIZE))

        pygame.draw.rect(displaysurface, RED,
                         pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        font = pygame.font.SysFont('Verdana', 25)
        text = font.render(str(score), True, GREEN)
        displaysurface.blit(text, [WIDTH/2, 10])

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.snake[0]
        # hit boundary
        if pt.x > self.w-BLOCK_SIZE or \
           pt.x < 0 or \
           pt.y > self.h - BLOCK_SIZE or \
           pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

