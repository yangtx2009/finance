"""
 This script uses low-pass filter to suppress high-frequency changes
"""
import pandas as pd
import sklearn
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
from datetime import datetime, timedelta
from scipy import signal as sci_signal
import tensorflow as tf

from Data.Stocks.ChineseStock import ChineseStock


def drawData(numpy_data, processed, title):
    if not (numpy_data is None):
        fig, axs = plt.subplots(2, 1)

        font = fm.FontProperties(fname='c:\\windows\\fonts\\simsun.ttc')
        axs[0].set_title(title, fontproperties=font)

        axs[0].plot('index', "value", data=numpy_data)
        ticks = np.linspace(0, numpy_data.shape[0] - 1, 20, dtype=int)
        axs[0].set_xticks(ticks)
        axs[0].set_xticklabels([numpy_data["times"][i] for i in ticks])
        axs[0].format_ydata = lambda x: '$%1.2f' % x  # format the price.

        axs[1].plot(numpy_data['index'], processed)
        ticks = np.linspace(0, numpy_data.shape[0] - 1, 20, dtype=int)
        axs[1].set_xticks(ticks)
        axs[1].set_xticklabels([numpy_data["times"][i] for i in ticks])
        axs[1].format_ydata = lambda x: '$%1.2f' % x  # format the price.

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
        plt.show()


def preprocessing(data):
    # remove nan
    data = data.dropna()
    print("data\n", data)

    # get name of stock
    titles = list(data.columns)
    titles.remove('times')

    # replace chinese name with 'value'
    data.columns.values[1] = "value"
    print("titles:\n", titles)

    # conver dataframe to structured numpy
    numpy_data = data.to_records()
    return titles, numpy_data


def showFakeData():
    startDate = datetime.fromordinal(733828)
    dateStr = startDate.strftime('%Y.%m.%d')
    print(dateStr)
    data = {"date": [(startDate + timedelta(i)).strftime('%Y.%m.%d') for i in range(20)],
            "value": [i * i for i in range(20)]}

    dataFrme = pd.DataFrame(data=data)
    print(dataFrme)

    fig, ax = plt.subplots()
    ax.plot('date', "value", data=dataFrme.to_records())
    fig.autofmt_xdate()
    plt.show()


def lowPassFilter(data):
    # https://www.cnblogs.com/xiaosongshine/p/10831931.html
    b, a = sci_signal.butter(8, 0.1, 'low', analog=False)  # 配置滤波器 8 表示滤波器的阶数
    filtedData = sci_signal.filtfilt(b, a, data)
    return filtedData


def showRandomCurve(stock):
    print("Showing random curve")
    data = stock.getRandomStock()

    titles, numpy_data = preprocessing(data)
    processed = lowPassFilter(numpy_data['value'])
    drawData(numpy_data, processed, titles[0])


def createLabels(input_length=30, output_length=7):
    '''
    @param input_length: in days
    @param output_length: in days
        start from 0 day.
        take il days, predict the next ol days
    @return:
    '''
    pass


if __name__ == '__main__':
    stock = ChineseStock()
    showRandomCurve(stock)
