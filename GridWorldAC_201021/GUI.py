import sys
import tkinter
import tkinter.font as font
import math
import random

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import Model as model
import Agent as agent

#グローバル
ROOT = None
CANVAS = None
FONT_C = None
FONT_B = None
CAN_SKIP = False

DIRS = {0 : 'r',
        1 : 'u',
        2 : 'l',
        3 : 'd'}
DIRVECS = {0 : (1, 0),
           1 : (0, 1),
           2 : (-1, 0),
           3 : (0, -1)}

#GUI起動
def SetUp(env, agent):
    root = tkinter.Tk()
    root.title(u"強化学習グリッドワールド第3章")
    root.geometry("1100x650")
        
    #キャンバス初期化
    canvas = tkinter.Canvas(root, width = 1000, height = 750)
    canvas.place(x=0, y=0)


    #グローバル変数代入
    global ROOT, CANVAS, FONT_C, FONT_B

    FONT_C = ("",15)
    FONT_B = ("",12)
    ROOT = root
    CANVAS = canvas
    Grid(env, agent)


def Start():
    ROOT.mainloop()

#画面全体を統括するクラス
class MainWindow:
    instance = None
    def __init__(self):
        #照す
        print("test")

#画面左のキャンバス用シングルトンクラス
class Grid:
    instance = None
    basePos = np.array([50, 50])
    posMag = np.array([150, 150])

    def __init__(self, grid, agent):

        #キャンバス初期化
        self.canvas = CANVAS
        self.root = ROOT
        self.env = grid
        self.agent = agent

        self.locuses = []
        self.infos = []
        Grid.instance = self
        self.canvas.place(x=200, y=0)
        self.SetSquire()

    #キャンパス更新
    def SetSquire(self):
        #矩形作成
        size = np.array([600, 450])
        point = Grid.basePos + size
        self.canvas.create_rectangle(*Grid.basePos, *point,  fill = "#ffffff", tag = "sq")
        self.canvas.create_rectangle(*Grid.GetPos(0, 2), *Grid.GetPos(1, 3),  fill = "#ffaaaa", tag = "v")
        self.canvas.create_rectangle(*Grid.GetPos(0, 1), *Grid.GetPos(1, 2),  fill = "#aaaaff", tag = "mv")
        self.canvas.create_rectangle(*Grid.GetPos(2, 1), *Grid.GetPos(3, 2),  fill = "#aaaaff", tag = "ban")
        return

    def GetPos(gridX, gridY):
        pos = np.array([gridX, (model.Environment.ySize - gridY)]) * Grid.posMag + Grid.basePos
        return pos

    def GetColor(num):
        num = int(num)
        if num > 255:
            num = 255
        elif num < -255:
            num = -255
        if num > 0:#価値がプラスなら
            return '#ff' + format(255 - int(num), '02x') + format(255 - int(num), '02x')
        else:
            return '#' + format(255 + int(num), '02x') + format(255 + int(num), '02x') + 'ff'

    def CheckLocus(self, states):
        if CAN_SKIP:
            if len(self.locuses) != 0:
                self.UnCheckLocus()
            return
        
        #もしデータ点がひとつなら線を引けないので省略
        if len(states) != 2:
            return

        #軌跡描写
        pos1 = Grid.GetPos(states[0].x, states[0].y)
        pos2 = Grid.GetPos(states[1].x, states[1].y)
        tags =f"{len(self.locuses)}_locus"
        self.canvas.create_line(*pos1, *pos2, width = 1.0, fill = '#ff0000', tag = tags)
        self.locuses.append(tags)

    #強調解除
    def UnCheckLocus(self):
        for i in self.locuses:
            self.canvas.delete(i)
        self.locuses = []

    def GetGrid(self, x, y):
        return self.squires[x][y]

    def SetInfo(self, x, y, angle, value):
        angle *= -1
        pos = Grid.GetPos(x, y)
        pos = np.matrix([[pos[0]],[pos[1]]])
        rot = np.matrix([[np.cos(angle), -np.sin(angle)],
                         [np.sin(angle), np.cos(angle)]])
        pos1 = rot * np.matrix([[25], [0]]) + pos
        pos2 = rot * np.matrix([[0], [5]]) + pos
        pos3 = rot * np.matrix([[0], [-5]]) + pos

        tags = f"{x}{y}info"
        self.canvas.create_polygon(*pos1.tolist(), *pos2.tolist(), *pos3.tolist(), fill = "#00aa00", tag = tags)
        textPos = Grid.GetPos(x, y) + np.array([15, 15])
        self.canvas.create_text(*textPos, text = f"{int(round(value * 100, 0))}", tag = tags + "text")
        self.infos.append(tags)
        self.infos.append(tags + "text")
    def ResetInfo(self):
        for tag in self.infos:
            self.canvas.delete(tag)
        self.infos = []

        



#画面右のウィジェット用静的クラス
class Widget:
    widgets = []
    toggles = []
    
    #ウィジェット配置
    base = np.array([50, 50, 30])

    #ウィジェット操作
    def ChangeToggle(bool):
        for toggle in Widget.widgets:
            if bool:
                toggle["state"] = "active"
            else:
                toggle["state"] = "disable"

    #文字ラベル用クラス
    class Label:
        labels = {}
        vars = {}

        #宣言用
        def Set(tag, pos, txt):
            var = tkinter.StringVar()
            var.set(txt)
            Widget.Label.vars[tag] = var
            label = tkinter.Label(ROOT, textvariable = var, width = 20)
            label.place(x = Widget.base[0], y = Widget.base[1] + pos * Widget.base[2])
            
            Widget.Label.vars[tag] = var
            Widget.Label.labels[tag] = label

            return

        #文字更新用
        def Rewrite(tag, txt):
            var = Widget.Label.vars.get(tag)
            var.set(txt)

    #エントリーボックス（文字入力欄）用クラス
    class Box:
        boxs = {}

        #宣言用
        def Set(tag, pos, txt, default, toggle):
            var = tkinter.StringVar()
            var.set(txt)
            label = tkinter.Label(ROOT, textvariable = var, width = 5)
            box = tkinter.Entry(width=5)
            label.pack()
            box.pack()
            Widget.Box.boxs[tag] = box
            box.insert(tkinter.END,str(default))
            label.place(x = Widget.base[0],y = Widget.base[1] + pos * Widget.base[2])
            box.place(x = Widget.base[0] + 50,y = Widget.base[1] + pos * Widget.base[2])

            if toggle:
                Widget.toggles.append(box)

        def Get(tag):
            box = Widget.Box.boxs.get(tag)
            return box.get()

    #ボタン用クラス
    class Button:
        #セット
        def Set(tag, pos, toggle, txt, func, *args):
            button = tkinter.Button(ROOT, text=txt, width=20, command=Widget.Button.DoFunc(func, *args))
            button.place(x = Widget.base[0], y = Widget.base[1] + pos * Widget.base[2])
            if toggle:
                Widget.widgets.append(button)

        #引数保持用の関数
        def DoFunc(func, *args):
            def inner():
                if args[0] == None:
                    func()
                else:
                    func(*args)
            return inner

class NNCanvas:
    search = None
    target = None
    train = None

    def __init__(self, NN, pos, delta):
        #初期設定
        self.isDelta = delta
        self.canvasSize = (600, 400)
        self.fontCenter = font.Font(size=15)
        self.fontBottom = font.Font(size=12)
        
        self.canvas = tkinter.Canvas(ROOT, width = self.canvasSize[0], height = self.canvasSize[1])
        self.canvas.place(x=pos[0], y=pos[1])

        self.nn = NN
        self.nn.nnwin = self
        self.checkedNode = []

        #ノードサイズ設定
        self.nodes = []
        sizes = NN.s
        bSizes = sizes.copy() #バイアスノード込みのノード数
        for i in range(len(bSizes) - 1):
            bSizes[i] += 1
        self.bSizes = bSizes

        for i in range(len(sizes)):
            u = NN.U[i]
            z = NN.Z[i]
            w = NN.W[i]
            b = NN.b[i]
            d = NN.Δ[i]
            nodes = []
            for j in range(sizes[i]):
                node = NNCanvas.Node(self.GetPos(j, bSizes[i], i, len(sizes)), self, j, i)
                nodes.append(node)
                node.SetNum([u[j], z[j], d[j]])
                if i != 0:
                    if self.isDelta:
                        node.SetButton()
                    node.SetWeights(w[j], b[j])

            #バイアスノード作成
            if i < len(sizes) - 1:
                node = NNCanvas.Node(self.GetPos(bSizes[i] - 1, bSizes[i], i, len(sizes)), self, j + 1, i)
                nodes.append(node)
                node.isSingle = True
                node.SetNum((0, 1, 0))
            self.nodes.append(nodes)


    class Node:
        def __init__(self, pos, NHWin, num, layer):
            self.isSingle = False #表示数値が1つかのフラグ
            self.num = num
            self.layer = layer

            self.nhwin = NHWin
            self.pos = np.array(pos)
            pos1 = self.pos - np.array([40, 40])
            pos2 = self.pos + np.array([40, 40])
            self.nhwin.canvas.create_oval(*pos1, *pos2, fill = "#ffffff")

            self.varNum = []
            self.varWeights = []


        def SetNum(self, nums):
            txt = [f"{round(nums[0], 2)}",f"{round(nums[1], 2)}", f"δ={round(nums[2], 2)}"]
            label = []
            if len(self.varNum) > 0:
                self.varNum[0].set(txt[0])
                self.varNum[1].set(txt[1])
                if self.nhwin.isDelta:
                    self.varNum[2].set(txt[2])
                return
            
            for num in range(3):
                if num == 2 and self.nhwin.isDelta != True:
                    break
                self.varNum.append(tkinter.StringVar())
                self.varNum[num].set(txt[num])
                label.append(tkinter.Label(self.nhwin.canvas, textvariable=self.varNum[num],width = 5, background="#ffffff"))
                delta = np.array([20, 20])
                delta2 = np.array([10, 10])
                if num == 0:
                   pos = self.pos - np.array([25, 25])
                elif num == 1:
                   pos = self.pos + np.array([-15, 10])
                elif num == 2:
                   pos = self.pos + np.array([10, -60])
                label[num].place(x = pos[0], y = pos[1])
            
        def SetWeights(self, weights, bias):
            #重みwとバイアスbの表示を更新する

            #位置取得
            pos = self.pos - np.array([80, (len(weights) + 1) * 10])

            #更新
            for i in range(len(weights) + 1):
                #ラベル作成
                if i == len(weights):
                    num = bias
                else:
                    num = weights[i]

                #既にラベルがあるなら値だけ更新
                if i < len(self.varWeights):
                    self.varWeights[i].set(round(num, 2))
                    continue

                var = tkinter.StringVar()
                self.varWeights.append(var)
                var.set(round(num, 2))

                label = tkinter.Label(self.nhwin.canvas, textvariable=var, width = 4)
                label.place(x = pos[0], y = pos[1])

                #直線作成
                sizes = self.nhwin.bSizes
                lPos = self.nhwin.GetPos(i, sizes[self.layer - 1], self.layer - 1, len(sizes))
                self.nhwin.canvas.create_line(*(pos+ np.array([-5, 10])), *(lPos + np.array([40, 0])))

                pos[1] += 20

        def SetButton(self):
            pos = self.pos.copy()
            pos += np.array([550, 60])
            button = tkinter.Button(ROOT, text = "*", width = 2, height = 1, command = NNCanvas.Node.DoFunc(self.nhwin.MakeGraph, *(self.layer, self.num)))
            button.place(x = pos[0], y = pos[1])
            #button.lower()

        def DoFunc(func, *args):
            def inner():
                if args[0] == None:
                    func()
                else:
                    func(*args)
            return inner

    def ResetVars(self):
        if CAN_SKIP:
            return
        NN =self.nn
        for i in range(len(NN.s)):
            u = NN.U[i]
            z = NN.Z[i]
            w = NN.W[i]
            b = NN.b[i]
            d = NN.Δ[i]
            for j in range(NN.s[i]):
                node = self.nodes[i][j]
                node.SetNum([u[j], z[j], d[j]])
                if i != 0:
                    node.SetWeights(w[j], b[j])

    def GetNodesByLayer(self, layerNum):
        return self.nodes[layerNum]


    def GetPos(self, num, numMax, l, lMax):
        flame = (20, 20)
        x = (self.canvasSize[0] - flame[0] * 2) / (lMax) * (l + 0.5) + flame[0]
        y = (self.canvasSize[1] - flame[1] * 2) / (numMax) * (num + 0.5) + flame[1]
     
        return np.array([x, y])

    def SetLayer(self, num, layer):
        nodes = []
        for i in range(layer.size):
            #ノード設置
            pos = self.GetPos(layer.size, num, i)
            node = NNCanvas.Node(pos, self, i)
            nodes.append(node)

            #出力層ならパス
            nLayer = layer.GetNext(1)
            if nLayer == None:
                continue

            for j in range(nLayer.size):
                #線設置
                nPos = self.GetPos(nLayer.size, num + 1, j)
                self.canvas.create_line(pos[0] + 100, pos[1] + 50, nPos[0], nPos[1] + 50)
        self.nodes[num] = nodes


    def CheckNodes(self, nodes):
        if CAN_SKIP:
            if len(self.checkedNode) != 0:
                self.Uncheck()
            return
        self.Uncheck()

        for i in range(len(nodes)):
            node = nodes[i]
            pos = node.pos
            name = f'node{i}'
            color = "#4000bf"
            pos1 = pos - np.array([40, 40])
            pos2 = pos + np.array([40, 40])
            self.canvas.create_oval(*pos1, *pos2, outline = color ,width = 3, tag = name)
            self.checkedNode.append(name)

    def CheckDelta(self, layerNum):
        if CAN_SKIP:
           return
        self.Uncheck()
        for i in range(self.bSizes[layerNum]):
            pos = self.GetPos(i, self.bSizes[layerNum], layerNum, len(self.bSizes))
            name = f'node{i}'
            color = "#4000bf"
            pos = pos + np.array([10, -60])
            pos1 = pos + np.array([-2, -2])
            pos2 = pos + np.array([42, 22])
            self.canvas.create_rectangle(*pos1, *pos2, outline = color ,width = 3, tag = name)
            self.checkedNode.append(name)

    def CheckWeight(self, layerNum):
        if CAN_SKIP:
           return
        self.Uncheck()
        pos = self.GetPos(0, self.bSizes[layerNum], layerNum, len(self.bSizes))
        name = f'weight'
        color = "#4000bf"
        pos = pos - np.array([83, 0])
        pos1 =np.array([pos[0] - 2, 30])
        pos2 =np.array([pos[0] + 42, 470])
        self.canvas.create_rectangle(*pos1, *pos2, outline = color ,width = 3, tag = name)
        self.checkedNode.append(name)


    def Uncheck(self):
        for name in self.checkedNode:
            self.canvas.delete(name)
        self.checkedNode = []

    def MakeGraph(self, layer, num):
        interval = type(self.nn).interval
        weights = self.nn.GetLogWeight(layer, num)
        x = []
        for i in range(len(weights[0])):
            x.append([])
        for i in range(len(weights)):
            for j in range(len(weights[0])):
               x[j].append(weights[i][j])

        print("--------")
        print(len(weights[0]))
        print(len(x[0]))
        print(len(range(0, len(weights) * interval, interval)))

        for i in range(len(weights[0])):
            plt.plot(range(0, len(x[i]) * interval, interval), x[i], label = f"w({layer}){i}{num}")
        plt.legend()
        plt.show()


class ListCanvas:
    instance = None

    def __init__(self, sampleList):
        #初期設定
        ListCanvas.instance = self
        self.canvasSize = (600, 600)
        self.pos = np.array([600, 400])
        self.fontCenter = font.Font(size=15)
        self.fontBottom = font.Font(size=12)
        
        self.canvas = tkinter.Canvas(ROOT, width = self.canvasSize[0], height = self.canvasSize[1])
        self.canvas.place(x=self.pos[0], y=self.pos[1])

        self.sampleList = sampleList
        self.vars = []
        self.varPlus = None
        self.SetLabels()

    #一括表示
    def ShowAll(self):
        len = self.sampleList.GetLen()
        for i in range(8):
            if len > i:
                self.ShowLabel(self.sampleList.list[i], i)
            else:
                self.ShowLabel(None, i)
        if len > 8:
            self.ShowPlus(len - 8)
        else:
            self.ShowPlus(0)

    #逐次的表示
    def Show(self):
        len = self.sampleList.GetLen()
        #もしリストが0なら
        if len == 0:
            return

        if len > 8:
                self.ShowPlus(len - 8)
                return
        for i in range(8):
            if len > i:
                self.ShowLabel(self.sampleList.list[i], i)
            else:
                self.ShowLabel(None, i)
    
                
    #一つ分の表示
    def ShowLabel(self, sample, num):
        if CAN_SKIP:
            return
        if sample == None:
            txt = ""
        else:
            txt = f"S({sample.state.x}, {sample.state.y}), a = {DIRS[sample.dir]}, r = {sample.reward}, S+1({sample.nState.x}, {sample.nState.y})"
        self.vars[num].set(txt)

    def ShowPlus(self, num):
        if CAN_SKIP and num %100 != 0:
            return

        self.varPlus.set(f"+{num}")

    def SetLabels(self):
        for i in range(8):
            txt = ""
            num = i + 1
            size = np.array([286, 50])
            start = np.array([50, 50])
            point1 = start.copy()
            point2 = start.copy()
            point1 += np.array([0, num * size[1]])
            point2 += np.array([size[0], (num + 1) * size[1]])
            self.canvas.create_rectangle(*point1, *point2,  fill = "#ffffff", tag = "Rect{num}")
            var = tkinter.StringVar()
            var.set(txt)
            lavel = tkinter.Label(self.canvas, textvariable=var, width = 25, font = ("",15), background="#ffffff")
            lavelpos = point1.copy()
            lavelpos += np.array([3, 12])
            lavel.place(x = lavelpos[0], y = lavelpos[1])
            self.vars.append(var)
        
        var = tkinter.StringVar()
        var.set(f"+{0}")
        lavel = tkinter.Label(self.canvas, textvariable=var, width = 20, font = ("",20))
        lavelpos = np.array([50, 520])
        lavel.place(x = lavelpos[0], y = lavelpos[1])
        self.varPlus = var

class InfoCanvas:
    instance = None

    def __init__(self):
        #初期設定
        InfoCanvas.instance = self
        self.canvasSize = (600, 600)
        self.pos = np.array([950, 480])
        
        self.canvas = tkinter.Canvas(ROOT, width = self.canvasSize[0], height = self.canvasSize[1])
        self.canvas.place(x=self.pos[0], y=self.pos[1])

        self.txt = ""
        pos = np.array([5, 5])
        self.var = tkinter.StringVar()
        self.var.set(self.txt)
        lavel = tkinter.Label(self.canvas, textvariable = self.var, width = 50, font = ("",15))
        lavel.place(x = pos[0], y = pos[1])

    #一括表示
    def SetText(self, txt):
        if CAN_SKIP:
            if self.txt != "画面更新停止":
                self.txt = "画面更新停止"
                self.var.set(self.txt)
            return
        self.txt = txt
        self.var.set(self.txt)
    def PlusText(self, txt):
        if CAN_SKIP:
            return
        self.txt += txt
        self.var.set(self.txt)
