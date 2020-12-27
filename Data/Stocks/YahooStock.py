from abc import ABC
import os
from Data.SqlClient import DatabaseClient
import pandas as pd
pd.set_option('display.max_columns', 20)
from datetime import datetime
import requests
from io import StringIO
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


class YahooStock(ABC):
    def __init__(self):
        super(YahooStock, self).__init__()
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        self.client = DatabaseClient()
        self.observationList = ["AAPL"]

    def getAllData(self, start="1980-12-12", end=None, show=False):
        for symbol in self.observationList:
            if not start:
                start = "1980-12-12"
            if not end:
                end = datetime.today().date().strftime("%Y-%m-%d")

            try:
                startTime = datetime.strptime(start, '%Y-%m-%d').replace(hour=1, minute=0, second=0, microsecond=0)
                endTime = datetime.strptime(end, '%Y-%m-%d').replace(hour=1, minute=0, second=0, microsecond=0)
                path = "https://query1.finance.yahoo.com/v7/finance/download/{0}?period1={1:d}&period2={2:d}&interval=1d" \
                       "&events=history&includeAdjustedClose=true".format(symbol,
                                                                          int(startTime.timestamp()),
                                                                          int(endTime.timestamp()))
                print(path)
                with requests.Session() as s:
                    content = StringIO(s.get(path).content.decode('utf-8'))
                    data = pd.read_csv(content)
                    # data["Date"].tolist()[::400]

                    if show:
                        self.show(data)
            except Exception as e:
                if isinstance(e, ValueError):
                    print("wrong date format")
                else:
                    print(e)

    def show(self, data):
        fig, ax = plt.subplots()
        line, = ax.plot(np.arange(len(data["Close"].tolist()[::200])), data["Close"].tolist()[::200], lw=1)
        ax.set_xticks(np.arange(len(data["Close"].tolist()[::200])))

        xLabels = data["Date"].tolist()[::200]
        xLabels = [xLabel if idx % 4 == 0 else '' for idx, xLabel in enumerate(xLabels)]
        ax.set_xticklabels(xLabels)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        fig.tight_layout()
        plt.show()


if __name__ == '__main__':
    # stock = YahooStock()
    # stock.getAllData()

    print(datetime.fromtimestamp(1608928401))
