import random
import numpy as np
from collections import deque

from components.game import DIRECTIONS, BLOCK_SIZE, LEFT, RIGHT, UP, DOWN

MAX_MEMORY = 100_000
BATCH_SIZE = 1000

class Agent:
    def __init__(self, model, force_new=False):
        self.n_games = 0
        self.epsilon_ini = 80
        self.epsilon_val = self.epsilon_ini
        self.max_games = 100
        self.curve = 5

        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = model
        saved_state = None if force_new else self.model.load()

        if saved_state:
            self.n_games = saved_state.get('n_games', 0)
            self.record = saved_state.get('record', 0)
        else:
            self.record = 0

    def get_state(self, game):
        head = game.snake[0]
        dir_idx = DIRECTIONS.index(game.direction)

        dir_straight = DIRECTIONS[dir_idx]
        dir_right = DIRECTIONS[(dir_idx + 1) % 4]
        dir_left = DIRECTIONS[(dir_idx - 1) % 4]

        point_straight = [head[0] + dir_straight[0] * BLOCK_SIZE, head[1] + dir_straight[1] * BLOCK_SIZE]
        point_right = [head[0] + dir_right[0] * BLOCK_SIZE, head[1] + dir_right[1] * BLOCK_SIZE]
        point_left = [head[0] + dir_left[0] * BLOCK_SIZE, head[1] + dir_left[1] * BLOCK_SIZE]

        state = [
            game.is_collision(point_straight),
            game.is_collision(point_right),
            game.is_collision(point_left),

            game.direction == LEFT,
            game.direction == RIGHT,
            game.direction == UP,
            game.direction == DOWN,

            game.food[0] < head[0],
            game.food[0] > head[0],
            game.food[1] < head[1],
            game.food[1] > head[1],
        ]

        return np.array(state, dtype=int)

    def get_action(self, state):
        self.epsilon_val = self.epsilon_ini * ((1 - min(self.n_games / self.max_games, 1)) ** self.curve)

        action = [0, 0, 0]
        if random.random() < self.epsilon_val / 100:
            move = random.randint(0, 2)
        else:
            prediction = self.model.predict(state)
            move = np.argmax(prediction)
            
        action[move] = 1
        return action

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_short_memory(self, state, action, reward, next_state, done):
        self.model.train(state, action, reward, next_state, done)

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        for state, action, reward, next_state, done in mini_sample:
            self.model.train(state, action, reward, next_state, done)
