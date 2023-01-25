"""
有限MDPを満たす環境を定義するファイル
各クラスをやり取りするState、Actionのデータ構造を示すとともに
(state, action)を受け取ってstateを返すenvironmentクラスを宣言する
"""

import sys
import numpy as np

#状態(State)クラス
class State:
    #使いまわし用

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        #Stateクラス同士が等しいかを定義する
        #x座標とy座標が等価なら等しい
        if other is None or type(self) != type(other):
            return False
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def GetReward(self):
        if 0 <self.x < 1 and 2 < self.y < 3:
            return 1
        if 0 <self.x < 1 and 1 < self.y < 2:
            return -1
        if 2 <self.x < 3 and 1 < self.y < 2:
            return -1

        x = self.x
        y = self.y
        if x < 0 or x >= Environment.xSize:
            return -1
        if y < 0 or y >= Environment.ySize:
            return -1

        return 0

    def IsPassable(self):
        if 2 <self.x < 3 and 1 < self.y < 2:
            return False
        return True

#行動(Action)クラス
class Action:
    
    def __init__(self, angle):
        self.angle = angle

    def __eq__(self, other):
        #Stateクラス同士が等しいかを定義する
        #x座標とy座標が等価なら等しい
        if self.angle == other.angle:
            return True
        return False


#環境(Environment)クラス
class Environment:
    xSize = 4
    ySize = 3
    startState = None
    vel = 0.2

    #初期化
    @classmethod
    def Initialize(cls):
        Environment.startState = State(3.5, 0.5)

    #stateとactionを受け取って次のstateを返す
    def __call__(self, state, action):
        angle = action.angle[0]
        pos = np.array([state.x, state.y])
        delta = np.array([np.cos(angle), np.sin(angle)]) * Environment.vel
        npos = pos + delta
        x = npos[0]
        y = npos[1]
        #範囲外か調べ、範囲外ならそのまま返す
        #if x < 0 or x >= Environment.xSize:
        #    return state
        #if y < 0 or y >= Environment.ySize:
        #    return state
        #通行可能か調べ、そうならそのまま返す
        nstate = State(x, y)
        '''
        if nstate.IsPassable() is False:
            l = x % 1.0
            r = 1.0 - l
            d = y % 1.0
            u = 1.0 - d
            delta = np.array([r, l, u, d])
            maxnum = np.argmin(delta)
            if maxnum == 0:
                return State(x + r, y)
            elif maxnum == 1:
                return State(x - l, y)
            elif maxnum == 2:
                return State(x, y + u)
            elif maxnum == 3:
                return State(x, y - d)
        '''
        return nstate