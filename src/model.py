import os
import json
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Input
from keras.optimizers import Adam
from keras.losses import MeanSquaredError

MODEL_FOLDER = './model'

class DQN:
    def __init__(self, input_size, hidden_size, output_size):
        self.model = Sequential([
            Input(shape=(input_size,)),
            Dense(hidden_size, activation='relu'),
            Dense(output_size)
        ])
        self.model.compile(optimizer=Adam(), loss=MeanSquaredError())

    def predict(self, state):
        state = np.array(state).reshape(1, -1)
        return self.model(state, training=False).numpy()

    def train(self, x, y):
        self.model.train_on_batch(np.array(x), np.array(y))

    def save(self, file_name='model.keras', stats=None):
        if not os.path.exists(MODEL_FOLDER):
            os.makedirs(MODEL_FOLDER)

        file_path = os.path.join(MODEL_FOLDER, file_name)
        self.model.save(file_path)

        if stats is not None:
            state_file = os.path.join(MODEL_FOLDER, 'stats.json')
            with open(state_file, 'w') as f:
                json.dump(stats, f)

    def load(self, file_name='model.keras'):
        file_path = os.path.join(MODEL_FOLDER, file_name)
        if os.path.exists(file_path):
            try:
                self.model = tf.keras.models.load_model(file_path)
            except Exception as e:
                return None
            state_file = os.path.join(MODEL_FOLDER, 'stats.json')
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    return json.load(f)
        return None

class DQNTrainer:
    def __init__(self, model: DQN, lr, gamma):
        self.model = model
        self.gamma = gamma

    def train_step(self, state, action, reward, next_state, done):
        state = np.array(state).reshape(1, -1)
        next_state = np.array(next_state).reshape(1, -1)
        target = self.model.predict(state)
        next_q = np.max(self.model.predict(next_state))

        Q_new = reward + self.gamma * next_q * (1 - int(done))
        target[0][np.argmax(action)] = Q_new

        self.model.train(state, target)
