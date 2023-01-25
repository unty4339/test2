"""
RLを進行するファイル
Agentクラスは内部にRLに必要な参照を保持し、Mainに逐次呼び出されながら学習を進める
"""

import sys
import random
import torch
import numpy as np

import Model as model
import NN as nn
import torch

CATCH_ERROR = False

class StepInfo:
    def __init__(self, reset, checkGrid):
        self.reset = reset
        self.getReward = 0
        self.checkGrid = checkGrid
        self.error = CATCH_ERROR

#エージェント
class Agent:
    #初期化
    def __init__(self, env):
        self.env = env

        self.actor = Actor()
        self.critic = Critic_v(0.90)

        self.Reset()
        
    def Reset(self):
        self.state = model.Environment.startState
        self.lastState = None
        self.lastAction = None

    def Do(self, epsilon):
        state = self.state
        print(f"({round(state.x, 2)}, {round(state.y, 2)})")
        
        #actorにstateを入れてactionを得る
        action = self.actor.GetAction(state, epsilon)
        #もし2回目以降なら
        if self.lastState is not None:
            #ls, la, s, aをcriticに与えつつ学習
            delta = self.critic.GetDelta(self.lastState, self.lastAction, state, action)

            #deltaでactorを訓練する
            self.critic.Train(self.lastState, self.lastAction, delta)
            self.actor.Train(self.lastState, self.lastAction, delta)

        #もし終端状態なら
        if state.GetReward() != 0:
            step = StepInfo(True, [self.state])
            step.reward = state.GetReward()
            self.Reset()
            return step
        
        #過去収納
        self.lastState = state
        self.lastAction = action
        
        #environmentにactionを入れる
        self.state = self.env(state, action)
        return StepInfo(False, [self.lastState, self.state])

    
    def GetAngle(self, state):
        return self.actor.GetAngle(state)

    def GetSigma(self, state):
        return self.actor.GetSigma(state)


    def GetV(self, state):
        return self.critic.GetV(state)

#アクター
class Actor:
    def __init__(self):
        self.ave_nn = nn.NeuralNetwork([2, 3, 1])
        self.dev_nn = nn.NeuralNetwork([2, 3, 1])
        return

    def GetAction(self, state, epsilon):
        #値取得
        input = torch.tensor([float(state.x), float(state.y)])
        ave = self.ave_nn(input)
        dev = self.dev_nn(input)
        dev = 2 / (1 + torch.exp(dev))

        if torch.isnan(ave):
            print("error")
            global CATCH_ERROR
            CATCH_ERROR = True

        #numpy変換
        ave = ave.clone().detach().cpu().numpy()
        dev = dev.clone().detach().cpu().numpy()

        angle = np.random.normal(
            loc   = ave,      # 平均
            scale = np.abs(dev) + epsilon,      # 標準偏差
            size  = 1
        )
        action = model.Action(angle)
        return action

    def Train(self, state, action, delta):
        #勾配除去
        self.ave_nn.optimizer.zero_grad()
        self.dev_nn.optimizer.zero_grad()

        #値取得
        input = torch.tensor([float(state.x), float(state.y)])
        ave = self.ave_nn(input)
        dev = self.dev_nn(input)
        dev = 2 / (1 + torch.exp(dev))
        x = torch.from_numpy(action.angle.astype(np.float32)).clone()

        e = torch.exp(- (x - ave) * (x - ave) / (2 * dev * dev))+ 10 ** -5
        c = 1 / torch.sqrt(2 *  3.141592653589793 * dev * dev)

        pi = e * c
        #print(f"pi = {pi} = {c} * {e}")
        pi = torch.log(pi) * -delta
        #print(f"logpi = {pi}")
        pi.backward()
        self.ave_nn.optimizer.step()
        self.dev_nn.optimizer.step()
        return

    def GetAngle(self, state):
        return self.ave_nn(torch.tensor([float(state.x), float(state.y)]))
    
    def GetSigma(self, state):
        return self.dev_nn(torch.tensor([float(state.x), float(state.y)]))

#クリティック
class Critic_v:
    def __init__(self, ganma):
        self.ganma = ganma
        self.nn = nn.NeuralNetwork([2, 3, 1])
        return

    def GetDelta(self, state, action, nextState, nextAction):
        #前回stateのQを取る
        input = torch.tensor([float(state.x), float(state.y)])
        v = self.nn(input)
        #print(f"v = {v}")
        
        #今回stateのQを取る
        if nextState.GetReward() != 0:
            nv = nextState.GetReward()
        else:
            input = torch.tensor([float(nextState.x), float(nextState.y)])
            nv = self.nn(input)

        delta = self.ganma * nv - v
        #print(f"GetDelta")
        #print(f"    q({state.x}, {state.y}, {action.num}) ={q}")
        #print(f"    nq({nextState.x}, {nextState.y}, {nextAction.num}) ={nq}")
        #print(f"    delta ={delta}")

        return delta.clone().detach().requires_grad_(False)[0]

    def Train(self, state, action, delta):
        self.nn.optimizer.zero_grad()
        
        #出力・勾配取得
        input = torch.tensor([float(state.x), float(state.y)])
        output = self.nn(input)
        output *= -delta
        output.backward()
        self.nn.optimizer.step()
        return

    def GetV(self, state):
        return self.nn(torch.tensor([float(state.x), float(state.y)]))


class StepData:
    xsize = 4
    ysize = 3
    class StateInfo:
        def __init__(self):
            self.G = 0
            self.N = 0
    
    def __init__(self):
        xsize = 4
        ysize = 3
        Gxya = []
        for x in range(model.Environment.xSize):
            Gya = []
            for y in range(model.Environment.ySize):
                Ga = []
                for a in range(4):
                    Ga.append(StepData.StateInfo())
                Gya.append(Ga)
            Gxya.append(Gya)
        self.statesInfo = Gxya
        self.T = 0

    def GetStateInfo(self, x, y, a):
        return self.statesInfo[x][y][a]

