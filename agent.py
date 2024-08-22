from main import SnakeGameAI, Direction, Point, BLOCK_SIZE
import torch
from model import Linear_QNet, QTrainer
from collections import deque
import random
import numpy as np

MAX_MEMORY = 100_100
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.nGames = 0  # number of games
        self.epsilon = 0  # controls random-ness, used for get_action
        self.gamma = 0  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # deque will call popleft() if memory exceeded
        self.model = Linear_QNet(11, 256, 3)  # TODO
        self.trainer = QTrainer(self.model, LR, self.gamma)  # TODO

    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)

        dir_l = (game.direction == Direction.LEFT)
        dir_r = (game.direction == Direction.RIGHT)
        dir_u = (game.direction == Direction.UP)
        dir_d = (game.direction == Direction.DOWN)

        danger_s = (dir_l and game._collision(point_l)) or (dir_r and game._collision(point_r))\
                   or (dir_u and game._collision(point_u)) or (dir_d and game._collision(point_d))
        danger_l = (dir_l and game._collision(point_d)) or (dir_r and game._collision(point_u))\
                   or (dir_u and game._collision(point_l)) or (dir_d and game._collision(point_r))
        danger_r = (dir_l and game._collision(point_u)) or (dir_r and game._collision(point_d))\
                   or (dir_u and game._collision(point_r)) or (dir_d and game._collision(point_l))

        food_l = game.food.x < head.x
        food_r = game.food.x > head.x
        food_u = game.food.y < head.y
        food_d = game.food.y > head.y

        state = [danger_s, danger_l, danger_r,
                 dir_l, dir_r, dir_u, dir_d,
                 food_l, food_r, food_u, food_d]
        return np.array(state, dtype=int)

    def get_action(self, state):
        self.epsilon = 80 - self.nGames
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
        else:
            state_0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(state_0)
            move = torch.argmax(prediction).item()  # cast max to int (0, 1, 2)

        final_move[move] = 1
        return final_move

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:  # make a batch
            sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            sample = self.memory
        # same as iterating through each item, but just faster
        states, actions, rewards, next_states, dones = zip(*sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


def train():
    plot_scores = []
    mean_scores = []
    total_score = 0
    best_score = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:  # training loop, runs forever until we quit script
        curr_state = agent.get_state(game)  # get current state

        final_move = agent.get_action(curr_state)  # get move based off current state

        reward, done, score = game.play_step(final_move)  # plays out move

        new_state = agent.get_state(game)  # get new state based on AI's move

        agent.train_short_memory(curr_state, final_move, reward, new_state, done)

        agent.remember(curr_state, final_move, reward, new_state, done)  # store state in deque

        if done:  # if game over, experienced replay (long memory)
            game.reset()  # reset the game
            agent.nGames += 1  # increase number of games
            agent.train_long_memory()

            if score > best_score:
                best_score = score
                agent.model.save()

            print("Game:", agent.nGames, ", Score:", score, ", Record:", best_score)

            # TODO: plot


if __name__ == "__main__":
    train()
