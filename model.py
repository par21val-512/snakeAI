import torch
from torch import nn, optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module): # Model
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):  # forward pass
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, filename='model.pth'):
        model_fldr_path = "./model"
        if not os.path.exists(model_fldr_path):
            os.makedirs(model_fldr_path)
        filename = os.path.join(model_fldr_path, filename)
        torch.save(self.state_dict(), filename)

class QTrainer():

    def __init__(self, model, lr, gamma):
        pass