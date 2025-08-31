import os
import json
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Input
from keras.optimizers import Adam
from keras.losses import MeanSquaredError

MODEL_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'models')

class DQN:
    def __init__(self, input_size, hidden_size, output_size, gamma=0.9):
        self.gamma = gamma
        self.model = Sequential([
            Input(shape=(input_size,)),
            Dense(hidden_size, activation='relu'),
            Dense(output_size)
        ])
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss=MeanSquaredError()
        )

    def predict(self, state):
        state = np.array(state).reshape(1, -1)
        return self.model(state, training=False).numpy()

    def train(self, state, action, reward, next_state, done):
        state = np.array(state).reshape(1, -1)
        next_state = np.array(next_state).reshape(1, -1)
        target = self.predict(state)
        next_q = np.max(self.predict(next_state))

        Q_new = reward + self.gamma * next_q * (1 - int(done))
        target[0][np.argmax(action)] = Q_new

        self.model.train_on_batch(np.array(state), np.array(target))

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
            except Exception:
                return None
            state_file = os.path.join(MODEL_FOLDER, 'stats.json')
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    return json.load(f)
        return None
