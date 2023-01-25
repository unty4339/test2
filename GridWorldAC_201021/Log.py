import matplotlib.pyplot as plt
import numpy as np

#logクラス
class Log:
    def MSE():
        teachData = []
        teachData.append([[72.9, None, None],
                     [65.6, 81, 81],
                     [59.1, None, 72.9],
                     [59.1, 65.6, 72.9]
                     ])
        teachData.append([[-100, None, None],
                     [81, 90, 90],
                     [65.6, None, 81],
                     [65.6, 72.9, 72.9]
                     ])
        teachData.append([[65.6, None, None],
                     [65.6, -100, 100],
                     [72.9, None, 90],
                     [65.6, 65.6, 81]
                     ])
        teachData.append([[65.6, None, None],
                    [72.9, 72.9, 81],
                    [65.6, None, 81],
                    [59.1, 59.1, 65.6]
                    ])
        trainingGrid = [[0, 0], [1, 0], [2, 0], [3, 0],
                                [1, 1],         [3, 1],
                                [1, 2], [2, 2], [3, 2]]

        num = 0
        sumDelta = 0
        sumQ = 0
        #教師データとの平均二乗誤差
        while True:
            x = trainingGrid[num][0]
            y = trainingGrid[num][1]
            state = Environment.instance.GetState(x, y)
            num += 1
            if num >= len(trainingGrid):
                #計算終了
                break        

            for dir in DIRS:
                q = teachData[dir][x][y]
                if q == None:
                    continue
                sumQ += 1
                lq = state.Q[dir]
                delta = q - lq

                D = Loss.Hober.Func([q], [lq])
                deltaSq = D[0]
                sumDelta += deltaSq

        return sumDelta / len(trainingGrid)

    def __init__(self):
        self.datasets = {}

    def AppendDataset(self, dataset):
        self.datasets[dataset.tag] = dataset

    def ShowDatas(self, tags):        
        for tag in tags:
            plt.plot(np.array(self.datasets[tag].value))
        plt.legend()
        plt.show()

    def ShowDatasAve(self, ave, max, min):
        for data in self.datasets.values:
            plt.plot(np.array(data))
        plt.legend()
        plt.show()



class DataSet:
    def __init__(self, tag, *, name = ""):
        self.tag = tag
        self.name = name
        self.value = []

    def Append(self, num):
        self.value.append(num)

    def GetAverage(self, span):
        ave = 0
        aves = []
        for i in range(len(self.value)):
            ave += self.value[i]
            if i - span >= 0:
                ave -= self.value[i - span]
            aves.append(ave / span)
        self.value = aves

