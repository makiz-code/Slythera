import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import json

class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth', stats=None):
        model_folder_path = 'model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        # Save model weights
        file_path = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_path)

        # Save game state (record, n_games)
        if stats is not None:
            state_file = os.path.join(model_folder_path, 'stats.json')
            with open(state_file, 'w') as f:
                json.dump(stats, f)

    def load(self, file_name='model.pth'):
        model_folder_path = 'model'
        file_path = os.path.join(model_folder_path, file_name)
        if os.path.exists(file_path):
            self.load_state_dict(torch.load(file_path))
            state_file = os.path.join(model_folder_path, 'stats.json')
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    return json.load(f)
        return None


class DQNTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        pred = self.model(state)
        target = pred.clone()

        # Bellman equation
        Q_new = reward + self.gamma * torch.max(self.model(next_state)) * (1-done)
        target[torch.argmax(action).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()
