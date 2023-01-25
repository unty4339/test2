import sys
import tkinter
import tkinter.font as font
import math
import random
import threading
import time
import torch

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import GUI as gui
import Model as model
import Agent as agent
import Log as log

#
#グローバル
#
#各定数の初期値
EPSILON = 0.0#閾値ε < 1
GANMA = 0.9#減衰率γ < 1
ALPHA = 0.1#学習率α < 1
COUNTRESET_PER = 3000
COUNTRESET_MAX = 1000#試行回数上限

COUNTMAX = 100

ENVIRONMENT = None

#変数
speed = 1
SKIP_SPEED = 20#画面処理を飛ばす下限速度
AFTER = None#実効予約中関数

#
#計算関係
#
#計算実行クラス
class Processor:
    instance = None

    def __init__(self):
        Processor.instance = self
        self.speed = 1
        self.ganma = 0
        self.alpha = 0
        self.countTrial = 0
        gridCanvas = gui.Grid.instance
        self.UpdateGrid()

        self.log =log.Log()
        self.rs = log.DataSet("r")
        self.log.AppendDataset(self.rs)

    def Reset():
        self = Processor.instance
        self.epsilon = float(gui.Widget.Box.Get('epsilon'))
        self.looper = self.GetYieldLoop() 
        self.countTrial = 0
        self.countReset = 0

    #下記の学習法定義クラスを引数として保持し繰り返し実行する
    def StartProcess(self):
        self.methodClass = AGENT
        self.epsilon = float(gui.Widget.Box.Get('epsilon'))
        self.ganma = float(gui.Widget.Box.Get('ganma'))
        self.alpha = float(gui.Widget.Box.Get('alpha'))
        #GUI.instance.ChangeToggle(False)

        if self.speed != 0:
            self.Process()


    #繰り返し呼び出して学習を進行する
    def Process(self):
        self.epsilon = float(gui.Widget.Box.Get('epsilon'))
        #格納した学習手法を実行し、返り値にGUIを更新するグリッドを得る
        for i in range(50):
            stepInfo = self.methodClass.Do(self.epsilon)
            
            if stepInfo.error:
                print("ERROR")
                self.speed = 0
            
            if stepInfo.reset:
                self.PlusTrialCount()
                self.rs.Append(stepInfo.reward)
                gui.Grid.instance.UnCheckLocus()

            if self.speed <500:
                break

        checkGrids = stepInfo.checkGrid

        #GUI
        if self.speed < 500:
            gui.Grid.instance.CheckLocus(checkGrids)

        #再帰
        if self.speed < 1:
            return
        AFTER = gui.ROOT.after(int(1000 / self.speed), self.Process)

    def ChangeSpeed(self, mag):
        global AFTER
        #現在の速度が0なら1に設定し、でなければmag倍
        if self.speed == 0 and mag >= 1:
            self.speed = 1
            if self.methodClass != None:
                AFTER = gui.ROOT.after(int(1000 / self.speed), self.Process)
        elif self.speed < 500 or mag < 1:
            self.speed *= mag
        
        #操作によって速度が1未満になったら一時停止
        if self.speed < 1:
            self.speed = 0
            if AFTER != None:
                gui.ROOT.after_cancel(AFTER)

        #速度が500以上でgui停止
        if self.speed > 500:
            gui.CAN_SKIP = True
        else:
            gui.CAN_SKIP = False
        
        #表示系更新
        gui.Widget.Label.Rewrite("speed", f"速度：{int(self.speed)}")
        if self.speed > 500:
            gui.Widget.Label.Rewrite("speed", f"速度：512 × 20")

    def PlusTrialCount(self):
        self.countTrial += 1
        gui.Widget.Label.Rewrite("countGoal", f"試行回数：{int(self.countTrial)}")
        self.alpha = float(gui.Widget.Box.Get("alpha"))
        if int(gui.Widget.Box.Get("countResetMax")) < self.countTrial:
            self.speed = 0

    def ShowGraph(self):
        self.rs.GetAverage(50)
        self.log.ShowDatas("r")

    def UpdateGrid(self):
        gui.Grid.instance.ResetInfo()
        for x in np.arange(0.165, model.Environment.xSize, 0.33):
            for y in np.arange(0.165, model.Environment.ySize, 0.33):
                state = model.State(x, y)
                #小数生成
                v = AGENT.GetV(state).tolist()[0]
                a = AGENT.GetAngle(state).tolist()[0]
                s = AGENT.GetSigma(state).tolist()[0]
                print(f"({round(x, 2)}, {round(y, 2)}), a = {round(a, 2)}, s = {round(s, 2)}")

                #テキスト生成
                txts = []
                colors = []
                gui.Grid.instance.SetInfo(x, y, a, v)
        return
    
    def UnupdateGrid(self):
        gui.Grid.instance.ResetInfo()
        return



#
#起動
#
model.Environment.Initialize()
ENVIRONMENT = model.Environment()
AGENT = agent.Agent(ENVIRONMENT)
gui.SetUp(ENVIRONMENT, AGENT)
Processor()

#ボタン配置
pos = 0
buttons = [('学習開始', None)]
for button in buttons:
    gui.Widget.Button.Set(button[0], pos, True, button[0], Processor.instance.StartProcess, button[1])
    pos += 1
pos += 1

entryboxs = [('epsilon','ε = ', EPSILON, True),
             ('ganma','γ = ', GANMA, True),
             ('alpha','α = ', ALPHA, False),
             ('countResetMax','更新上限', COUNTRESET_MAX, False),
             
             
             ]
for box in entryboxs:
    gui.Widget.Box.Set(box[0] ,pos, box[1], box[2], box[3])
    pos += 1


labels = [('countGoal','ゴール回数：0'),
          ('countReset','更新回数：0'),
          ('speed','速度：1')]
for label in labels:
    gui.Widget.Label.Set(label[0] ,pos, label[1])
    pos += 1

buttons = [('加速', Processor.instance.ChangeSpeed, 2),
          ('減速', Processor.instance.ChangeSpeed, 0.5),
          ('hoji', Processor.instance.UpdateGrid, None),
          ('hihyo', Processor.instance.UnupdateGrid, None),
          ('graph', Processor.instance.ShowGraph, None),]
for button in buttons:
    gui.Widget.Button.Set(button[0], pos, False, button[0], button[1], button[2])
    pos += 1

gui.Start()