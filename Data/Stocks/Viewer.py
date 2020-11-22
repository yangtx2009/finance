import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

from Data.Stocks.MyCheckButtons import MyCheckButtons
from Data.Stocks.Stock import Stock


class Viewer:
    def __init__(self):
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        self.stock = Stock()
        self.stock.calculateIndustryPerformance()

        data = self.stock.selected_data.to_dict()
        self.times = data.pop("times")
        self.timesList = [value for (key, value) in sorted(self.times.items())]

        # font = fm.FontProperties(fname='c:\\windows\\fonts\\simsun.ttc')
        matplotlib.rc('font', family='simsun')
        matplotlib.rcParams.update({'font.size': 8})

        self.colors = self.generateColors(len(data))

        fig, ax = plt.subplots()
        plt.subplots_adjust(left=0.2)
        self.lines = list()
        for index, (key, value) in enumerate(data.items()):
            stock = [value1 for (key1, value1) in sorted(value.items())]
            line, = ax.plot(self.timesList, stock, visible=False, lw=1, label=key, color=self.colors[index])
            self.lines.append(line)

        ax.xaxis.set_major_locator(MultipleLocator(5))
        # ax.xaxis.set_minor_locator(AutoMinorLocator())

        # rax = plt.axes([0.05, 0.15, 0.1, 0.7])
        rax = plt.axes([0.05, 0.1, 0.1, 0.8])  # x0, y0, x1, y1
        self.labels = [str(line.get_label()) for line in self.lines]
        visibility = [line.get_visible() for line in self.lines]
        colors = [line.get_color() for line in self.lines]
        print("colors", colors[0])
        check = MyCheckButtons(rax, self.labels, bw=0.04, colors=colors, actives=visibility)
        check.on_clicked(self.func)

        plt.show()

    def func(self, label):
        index = self.labels.index(label)
        self.lines[index].set_visible(not self.lines[index].get_visible())
        plt.draw()

    def generateColors(self, n):
        ret = []
        VNum = 10
        SNum = n // 10
        rest = n % 10
        offset = 120
        for i in range(VNum):
            h = int(i * 255 / VNum)
            for j in range(SNum):
                s = int(offset + j * (255 - offset) / SNum)
                ret.append('#%02x%02x%02x' % self.hsv_to_rgb(h / 255., s / 255., 200 / 255.))
        for k in range(rest):
            t = int(k / rest)
            ret.append('#%02x%02x%02x' % self.hsv_to_rgb(t, t, t))
        return ret

    def hsv_to_rgb(self, h, s, v):
        if s == 0.0:
            v *= 255
            return int(v), int(v), int(v)
        i = int(h * 6.)  # XXX assume int() truncates!
        f = (h * 6.) - i
        p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))))
        v *= 255
        i %= 6
        if i == 0:
            return int(v), int(t), int(p)
        if i == 1:
            return int(q), int(v), int(p)
        if i == 2:
            return int(p), int(v), int(t)
        if i == 3:
            return int(p), int(q), int(v)
        if i == 4:
            return int(t), int(p), int(v)
        if i == 5:
            return int(v), int(p), int(q)


if __name__ == '__main__':
    viewer = Viewer()
