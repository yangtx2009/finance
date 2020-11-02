# from bin.x64.iFinDPy import *
import urllib.request
import json
from abc import ABC
import pprint
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import sys
import gzip

from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import time
import itertools

import matplotlib.font_manager as font_manager
pd.set_option('display.max_columns', 20)
import copy
from sklearn import preprocessing
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import random
import math
import tqdm

from WebScraper import LoadFinishCondition, LoadThread
from SqlClient import DatabaseClient

class Stock(ABC):
    # https://www.jianshu.com/p/2f45fcb44771
    def __init__(self):
        super(Stock, self).__init__()
        self.averaged = {}
        self.selected_data = None
        self.client = DatabaseClient()

        self.m_industryList = pd.DataFrame(columns=["industry", "link"])
        self.loadIndustryListFromDB()

        self.m_stockList = pd.DataFrame(columns=["industry", "name", "symbol"])
        self.loadStockListFromDB()

        # self.m_hsIndexTotal = None
        # self.m_hsIndexToday = None
        # self.readHSIndex(True)
        #
        # self.m_szList = None
        # self.m_shAList = None
        # self.m_shSciInnoList = None

    def loadIndustryListFromDB(self):
        df = self.client.readTableNames()

        if "industry" in df.values:
            self.m_industryList = self.client.readTable("industry")
            print("industries\n", self.m_industryList)
        else:
            self.readIndustryList()
            self.client.createTable("industry", ["industry VARCHAR(255)", "link VARCHAR(255)"], "industry")
            self.client.storeData("industry", self.m_industryList, "append")
            self.client.showTable("industry")

    def loadStockListFromDB(self):
        df = self.client.readTableNames()
        if "stock" in df.values:
            print("Stock already exists in database")
            self.m_stockList = self.client.readTable("stock")
            print("stocks\n", self.m_stockList)
        else:
            print("Cannot find 'stock' in database. Creating it ...")
            self.client.createTable("stock", ["industry VARCHAR(255)", "name VARCHAR(255)", "symbol VARCHAR(255)"],
                                    "symbol")
            self.readStockList()
            self.m_stockList = self.m_stockList.drop_duplicates(subset=['symbol'])
            self.client.storeData("stock", self.m_stockList, "append")
            self.client.showTable("stock")

    def readHSIndex(self, p_draw=False):
        url = "http://img1.money.126.net/data/hs/kline/day/times/1399001.json"
        with urllib.request.urlopen(url) as url_file:
            l_jsonData = json.loads(url_file.read().decode())
            self.m_hsIndexTotal = pd.DataFrame(data={"closes": l_jsonData["closes"], "times": l_jsonData["times"]})
            print("hsIndex total", self.m_hsIndexTotal.head(5))

        url = "http://img1.money.126.net/data/hs/time/today/1399001.json"
        with urllib.request.urlopen(url) as url_file:
            l_jsonData = json.loads(url_file.read().decode())
            print(l_jsonData.keys())
            # self.m_hsIndexToday = pd.DataFrame(data={"data": data["closes"], "times": data["times"]})
            # print("hsIndex today", self.m_hsIndexToday.head(5))

        if p_draw:
            self.m_hsIndexTotal.plot(x="times", y="closes", title="HS index", figsize=(10,4))
            plt.title("HS index", fontproperties='SimHei', fontsize='large')
            plt.show()

    def readIndustryList(self):
        print("Reading industry list ...")
        url = "http://stock.eastmoney.com/hangye.html"
        r = requests.get(url)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')

        hangye_div = soup.find('div', {'class': 'hot-hy-list'})
        children = hangye_div.findChildren("a", recursive=True)

        for child in children:
            original_link = child.get("href")
            code = int(original_link.split(".")[0].split("hy")[1])
            link = "http://quote.eastmoney.com/center/boardlist.html#boards-BK{:04d}1".format(code)
            self.m_industryList = self.m_industryList.append({"industry":child.get("title"), "link":link},
                                                             ignore_index=True)

        print("Created new industry list")
        # self.m_industryList.to_csv("IndustryList.csv")
        # print(self.m_industryList["industry"], "\n")

    def xpath_soup(self, element):
        """
        Generate xpath of soup element
        :param element: bs4 text or node
        :return: xpath as string
        """
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            """
            @type parent: bs4.element.Tag
            """
            previous = itertools.islice(parent.children, 0, parent.contents.index(child))
            xpath_tag = child.name
            xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
            components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)

    def readStockList(self):
        """
            use selenium to wait for javascript in webpage loading data
        :return:
        """
        print("Reading stock list ...")
        startTime = time.time()

        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.add_argument("--headless")
        fireFoxOptions.add_argument('--disable-gpu')
        fireFoxOptions.add_argument('--no-sandbox')
        browser = webdriver.Firefox(firefox_options=fireFoxOptions, executable_path=r"geckodriver.exe")
        for index, row in tqdm.tqdm(self.m_industryList.iterrows()):
            print("{}/{}: Getting {} information ({})".format(index, len(self.m_industryList), row["industry"], row['link']))
            industry_url = row['link']
            browser.get(industry_url)
            # time.sleep(5)
            WebDriverWait(browser, timeout=10).until(LoadFinishCondition()) # , poll_frequency=5
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            while True:
                next_button_soup = None
                self.findStocks(soup, row["industry"])
                next_button_soup = soup.find("a", {"class", "next paginate_button"})
                if next_button_soup:
                    xpath = self.xpath_soup(next_button_soup)
                    next_button = browser.find_element_by_xpath(xpath)
                    if next_button:
                        next_button.click()
                        print("To next page")
                        WebDriverWait(browser, timeout=10).until(LoadFinishCondition())
                        html = browser.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                    else:
                        print("Cannot find button component!")
                        break
                else:
                    print("Cannot find next page button!")
                    break
            self.m_stockList.to_csv("StockList.csv")
        browser.quit()
        print("Created new industry list")
        # self.m_stockList.to_csv("StockList.csv")
        print(self.m_stockList.head(5))

        timeElapsed = (time.time() - startTime)
        print("The loading of stock list takes {} seconds".format(timeElapsed))

    def findStocks(self, soup, key):
        table = soup.find('table', {'id': 'table_wrapper-table'})
        stocks = table.findChild("tbody", recursive=True).findChildren("tr", recursive=True)

        for stock in stocks:
            values = stock.findChildren("td", recursive=True)
            temp = {"industry": key}
            for idx, value in enumerate(values):
                if idx == 1:
                    temp["symbol"] = value.string
                elif idx == 2:
                    temp["name"] = value.string
            # print("adding stock:", temp)
            self.m_stockList = self.m_stockList.append(temp, ignore_index=True)

    def correctTimes(self):
        industries = self.m_stockList.groupby("industry")
        for name, industry in industries:
            filename = os.path.join("industries", "{}.csv".format(name))
            data = pd.read_csv(filename)
            data["times"] = ["{}.{}.{}".format(str(t)[:4], str(t)[4:6], str(t)[6:8]) for t in data["times"].tolist()]
            data.to_csv(filename)
        print(data.head(10))

    def chunkIt(self, seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg
        return out

    def calculateIndustryPerformance(self, threadNum=30, showRows=100):
        print("Calculating industry performance ...")
        industries = self.m_stockList.groupby("industry")

        if not os.path.exists("industries"):
            os.makedirs("industries")

        industryNames = list(industries.groups.keys())
        grouped = self.chunkIt(industryNames, threadNum)
        threads = list()
        for n in range(threadNum):
            threads.append(LoadThread(n, self, grouped[n]))
            threads[n].start()

        print("Waiting for reading stocks ...")
        for n in range(threadNum):
            threads[n].join()

        joined = None
        for idx, (name, data) in enumerate(self.averaged.items()):
            averaged_industry = pd.DataFrame(columns=["times", name])
            averaged_industry["times"] = data["times"].tolist()
            temp = copy.deepcopy(data).drop("times", axis=1).mean(axis=1)
            averaged_industry[name] = temp

            if joined is None:
                joined = averaged_industry
            else:
                joined = pd.merge(joined, averaged_industry, on="times", how='outer')

        joined = joined.sort_values(by="times")
        joined.to_csv("joined.csv")

        # fig, ax = plt.subplots()
        # meanData = joined.drop("times", axis=1)
        # meanData = meanData.mean(axis=0)
        # print("meanData", meanData)
        # font = font_manager.FontProperties(family='SimHei', style='normal', size=6)
        # meanData.plot.bar(ax=ax, grid=True)
        # plt.xticks(fontname="SimHei")
        # plt.legend(loc='best', ncol=4, prop=font)
        # plt.title("Industries", fontproperties='SimHei', fontsize='large')
        # plt.show()

        min_max_scaler = preprocessing.MinMaxScaler()
        self.selected_data = joined.tail(showRows)

        # # print("current_data column title:", self.selected_data.columns)
        # scaled_array = min_max_scaler.fit_transform(self.selected_data.drop(["times"], axis=1))
        # df_normalized = pd.DataFrame(scaled_array)
        # df_normalized.columns = list(self.selected_data.drop(["times"], axis=1).columns.values)
        # df_normalized["times"] = self.selected_data["times"].values
        # self.selected_data = df_normalized

        # industry_names = self.averaged.keys()
        # fig, ax = plt.subplots()
        # for name in industry_names:
        #     ax = df_normalized.plot(ax=ax, kind='line', x='times', y=name, label=name, grid=True)
        # font = font_manager.FontProperties(family='SimHei', style='normal', size=6)
        # plt.legend(loc='best',ncol=4, prop=font)
        # plt.title("Industries", fontproperties='SimHei', fontsize='large')
        # plt.show()

    def getRandomStock(self):
        industries = self.m_stockList.groupby("industry")
        industryNames = list(industries.groups.keys())
        industryName = random.sample(industryNames,1)[0]
        filename = os.path.join("industries", "{}.csv".format(industryName))
        if os.path.exists(filename):
            data = pd.read_csv(filename)
            titles = list(data.columns)
            titles.remove("times")
            return data[["times",titles[0]]]
        else:
            print("Cannot find {} in industries directory".format(filename))
            return None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        wicon = QtGui.QIcon("resources/Artboard 1.png")
        self.setWindowIcon(wicon)

        self.stock = Stock()
        self.colorMap = None

        self.stock.calculateIndustryPerformance()

        self.mainWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainWidget)

        mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainWidget.setLayout(mainLayout)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setAspectLocked(10)
        mainLayout.addWidget(self.graphWidget,5)

        controlWidget = QtWidgets.QWidget()
        mainLayout.addWidget(controlWidget,1)

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

        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature = [30,32,34,32,33,31,29,32,35,45]

        self.graphWidget.setBackground('w')

        # print(type(self.graphWidget.plot(hour, temperature)))
        self.curves = {}

        # self.refreshList()

    def setYRange(self, range):
        self.enableAutoRange(axis='y')
        self.setAutoVisible(y=True)

    def colors(self, n):
        ret = []
        VNum = 10
        SNum = n//10
        rest = n%10
        offset = 120
        for i in range(VNum):
            h = int(i * 255 / VNum)
            for j in range(SNum):
                s = int(offset + j * (255-offset) / SNum)
                ret.append((h, s, 200))
        for k in range(rest):
            t = int(k * 255 / rest)
            ret.append((t, t, t))
        return ret

    def refreshList(self):
        temp = self.stock.selected_data.to_dict()
        # self.checkBoxDict = {'保险': {0: 72.26, 1: 72.27285714285713, 2: 73.07000000000001, ...
        self.times = temp.pop("times")

        self.times = [value for (key, value) in sorted(self.times.items())]
        print("times", self.times)


        for key, value in temp.items():
            self.dataDict[key] = [value1 for (key1, value1) in sorted(value.items())]

        self.colorMap = self.colors(len(self.dataDict))

        for key, value in self.dataDict.items():
            self.checkBoxListWidget.addItem(key)

        for i in range(self.checkBoxListWidget.count()):
            item = self.checkBoxListWidget.item(i)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
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
                self.curves[text] = self.graphWidget.plot(np.arange(num),
                                                         self.dataDict[text], pen=pg.mkPen(color=color, width=2))
                self.curves[text].setVisible(checked)

        ax = self.graphWidget.getAxis('bottom')
        ticks = [list(zip(range(0, num, 10), [self.times[i] for i in range(0, num, 10)]))]
        ax.setTicks(ticks)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # stock = Stock()
    # # stock.correctTimes()
    # stock.calculateIndustryPerformance()
    # # stock.readStock(stock.m_stockList["symbol"].tolist()[10], stock.m_stockList["industry"].tolist()[10])
    main()

    # stock = Stock()
