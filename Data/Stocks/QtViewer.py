from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import os
import sys

from Data.Stocks.ChineseStock import ChineseStock


class QtViewer(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(QtViewer, self).__init__(*args, **kwargs)
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        wicon = QtGui.QIcon(os.path.join(self.localDir, "icons", "Artboard 1.png"))
        self.setWindowIcon(wicon)

        self.stock = ChineseStock()
        self.colorMap = None
        self.lastPen = None
        self.lastItem = None
        self.times = None
        self.timesList = None

        self.stock.calculateIndustryPerformance()

        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)

        mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainWidget.setLayout(mainLayout)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setAspectLocked(10)
        mainLayout.addWidget(self.graphWidget, 5)

        controlWidget = QtWidgets.QWidget()
        mainLayout.addWidget(controlWidget, 1)

        controlLayout = QtWidgets.QVBoxLayout(self)
        controlWidget.setLayout(controlLayout)

        self.checkBoxListWidget = QtWidgets.QListWidget(self)
        self.dataDict = {}
        # self.checkBoxList = []
        controlLayout.addWidget(self.checkBoxListWidget)
        self.loadButton = QtWidgets.QPushButton("load", self)
        self.refreshButton = QtWidgets.QPushButton("refresh", self)
        self.loadButton.clicked.connect(self.refreshList)
        self.refreshButton.clicked.connect(self.updatePlot)
        controlLayout.addWidget(self.loadButton)
        controlLayout.addWidget(self.refreshButton)

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]

        self.graphWidget.setBackground('w')
        self.graphWidget.scene().sigMouseClicked.connect(self.curveClicked)
        self.curves = {}

    def setYRange(self, range):
        self.enableAutoRange(axis='y')
        self.setAutoVisible(y=True)

    def colors(self, n):
        ret = []
        VNum = 10
        SNum = n // 10
        rest = n % 10
        offset = 120
        for i in range(VNum):
            h = int(i * 255 / VNum)
            for j in range(SNum):
                s = int(offset + j * (255 - offset) / SNum)
                ret.append((h, s, 200))
        for k in range(rest):
            t = int(k * 255 / rest)
            ret.append((t, t, t))
        return ret

    def refreshList(self):
        temp = self.stock.selected_data.to_dict()
        # self.checkBoxDict = {'保险': {0: 72.26, 1: 72.27285714285713, 2: 73.07000000000001, ...
        self.times = temp.pop("times")
        self.timesList = [value for (key, value) in sorted(self.times.items())]

        for key, value in temp.items():
            self.dataDict[key] = [value1 for (key1, value1) in sorted(value.items())]

        self.colorMap = self.colors(len(self.dataDict))

        for key, value in self.dataDict.items():
            self.checkBoxListWidget.addItem(key)

        for i in range(self.checkBoxListWidget.count()):
            item = self.checkBoxListWidget.item(i)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)  # Unchecked
            color = QtGui.QColor()
            color.setHsv(*self.colorMap[i])
            item.setBackground(QtGui.QBrush(color))
        self.checkBoxListWidget.itemChanged.connect(self.updatePlot)
        self.updatePlot()

    def updatePlot(self):
        # self.graphWidget.clear()
        num = None
        for i in range(self.checkBoxListWidget.count()):
            item = self.checkBoxListWidget.item(i)
            text = item.text()
            checked = item.checkState()

            num = len(self.dataDict[text])
            if text in self.curves:
                self.curves[text].setVisible(checked)
            else:
                color = QtGui.QColor()
                color.setHsv(*self.colorMap[i])
                item = self.graphWidget.plot(np.arange(num), self.dataDict[text], pen=pg.mkPen(color=color, width=1))
                self.curves[text] = item
                print(text, self.curves[text].curve)
                self.curves[text].setVisible(checked)

        ax = self.graphWidget.getAxis('bottom')
        ticks = [list(zip(range(0, num, 10), [self.timesList[i] for i in range(0, num, 10)]))]
        ax.setTicks(ticks)
        self.graphWidget.enableAutoRange(y=True)

    def curveClicked2(self):
        print("curveClicked2")

    def curveClicked(self, ev):
        print("clicked")
        if self.lastItem is not None:
            self.lastItem.setPen(self.lastPen)

        # print(self.graphWidget.scene().itemsNearEvent(ev))
        for item in self.graphWidget.scene().itemsNearEvent(ev):
            if isinstance(item, pg.PlotCurveItem):
                self.lastPen = item.opts["pen"]
                self.lastItem = item
                item.setPen(pg.mkPen(item.opts["pen"].color(), width=2, style=QtCore.Qt.DashLine))

                # name = list(self.curves.keys())[list(self.curves.values()).index(item)]
                for index, (name, curve) in enumerate(self.curves.items()):
                    if curve.curve == item:
                        print("selected curve", name)
                        self.checkBoxListWidget.setCurrentRow(index)
                break


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = QtViewer()
    main.show()
    sys.exit(app.exec_())