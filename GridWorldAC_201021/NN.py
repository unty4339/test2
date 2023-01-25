"""
pytorchを利用したNNの挙動を定義するファイル
"""


import torch
import torch.nn

class NeuralNetwork(torch.nn.Module):
    def __init__(self, size):
        super().__init__()
        self.fcs = []
        self.fc1 = torch.nn.Linear(size[0], size[1])
        self.fc2 = torch.nn.Linear(size[1], size[2])
        self.sigmoid = torch.nn.Sigmoid()
        self.optimizer = torch.optim.SGD(self.parameters(), lr=0.02)

    def forward(self, x):
        x = self.fc1(x)
        x = self.sigmoid(x)
        x = self.fc2(x)
        return x

    def train(self, state, action, delta):
        #勾配除去
        self.optimizer.zero_grad()
        
        #出力・勾配取得
        input = torch.tensor([float(state.x), float(state.y)])
        output = self(input)
        output[action.num] *= -delta
        output[action.num].backward()
        self.optimizer.step()
        #print(f"train({state.x}, {state.y})")
        #for param in self.parameters():
        #    print(param.grad)


        return
#実行する