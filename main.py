import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.SysFont('times', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

BLOCK_SIZE = 20
STARTING_SPEED = 10


# Snake Game Class
class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w  # width
        self.h = h  # height
        self.speed = STARTING_SPEED
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        self.reset()
        '''x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        if Point(x, y) in self.snake:
            self.bomb = Point(x + BLOCK_SIZE, y + BLOCK_SIZE)
        else:
            self.bomb = Point(x, y)'''

    def reset(self):  # init game state
        self.direction = Direction.RIGHT  # start facing right
        self.head = Point(self.w / 2, self.h / 2)  # snake head position
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE  # clip food to grid so that snake can "eat" it
        y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        # 1. User input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move snake
        self._move(action)
        self.snake.insert(0, self.head)  # insert updated head position

        # 3. check if game_over
        reward = 0
        game_over = False
        if self._collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. see if we need to place new food
        if self.head == self.food:
            reward = 10
            self.score += 5
            self.speed += 3
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and return score
        self._update_ui()
        self.clock.tick(self.speed)
        return reward, game_over, self.score

    def _collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt in self.snake[1:]:
            return True
        elif pt.x > self.w - BLOCK_SIZE or pt.x < 0:
            return True
        elif pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        else:
            return False

        # elif self.head == self.bomb:
        #    return True

    def _update_ui(self):
        self.display.fill(BLACK)

        '''pygame.draw.rect(self.display, RED, pygame.Rect(
            self.bomb.x, self.bomb.y, BLOCK_SIZE, BLOCK_SIZE))'''

        for segment in self.snake:
            pygame.draw.rect(self.display, BLUE, pygame.Rect(
                segment.x, segment.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, LIGHT_BLUE, pygame.Rect(
                (segment.x + 4), (segment.y + 4), BLOCK_SIZE - 8, BLOCK_SIZE - 8))

        pygame.draw.rect(self.display, GREEN, pygame.Rect(
            self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()  # flip updates whole screen

    def _move(self, action):
        # action space:
        # [1, 0, 0] => straight
        # [0, 1, 0] => right
        # [0, 0, 1] => left
        dirs = [Direction.RIGHT, Direction.DOWN, Direction.left, Direction.UP]
        idx = dirs.index(self.direction) # get index of previous direction
        x = self.head.x
        y = self.head.y
        if np.array_equal(action, [1, 0, 0]):
            direction = dirs[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4 # right turn r -> d -> l -> u
            direction = dirs[next_idx]
        else:
            next_idx = (idx - 1) % 4 # left turn r-> u -> l -> d
            direction = dirs[next_idx]

        self.direction = direction  # update direction

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)
