from dotenv import load_dotenv
load_dotenv()

import random
import numpy as np
from collections import deque

from game import SnakeGame, DIRECTIONS, BLOCK_SIZE, LEFT, RIGHT, UP, DOWN
from model import DQN, DQNTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)

        self.model = DQN(11, 256, 3)
        saved_state = self.model.load()
        self.trainer = DQNTrainer(self.model, lr=LR, gamma=self.gamma)

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
        self.epsilon = 80 - self.n_games
        action = [0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            action[move] = 1
        else:
            prediction = self.model.predict(state)
            move = np.argmax(prediction)
            action[move] = 1

        return action

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        for state, action, reward, next_state, done in mini_sample:
            self.trainer.train_step(state, action, reward, next_state, done)


def train():
    agent = Agent()
    env = SnakeGame()
    record = agent.record

    try:
        while True:
            state_old = agent.get_state(env)
            action = agent.get_action(state_old)
            reward, done, score = env.step(action, agent.n_games, record)

            if score == 'quit':
                agent.model.save(stats={'record': record, 'n_games': agent.n_games})
                break

            if score == 'reset_agent':
                agent = Agent()
                record = agent.record
                env.reset()
                continue

            state_new = agent.get_state(env)
            agent.train_short_memory(state_old, action, reward, state_new, done)
            agent.remember(state_old, action, reward, state_new, done)

            if done:
                env.reset()
                agent.n_games += 1
                agent.train_long_memory()

                if score > record:
                    record = score
                    agent.model.save(stats={'record': record, 'n_games': agent.n_games})

    except KeyboardInterrupt:
        agent.model.save(stats={'record': record, 'n_games': agent.n_games})

if __name__ == '__main__':
    train()
