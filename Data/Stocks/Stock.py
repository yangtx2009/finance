# from bin.x64.iFinDPy import *
import urllib.request
import json
from abc import ABC
import matplotlib.pyplot as plt
import pandas as pd
import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import time
import itertools

import copy
from sklearn import preprocessing
import random
import tqdm
import numpy as np

from Data.Stocks.Loader import LoadFinishCondition, LoadThread
from threading import Lock
from Data.SqlClient import DatabaseClient
pd.set_option('display.max_columns', 20)


class Stock(ABC):
    # https://www.jianshu.com/p/2f45fcb44771
    def __init__(self, db_conn, db_abs_path):
        super(Stock, self).__init__()
        self.db_conn = db_conn
        self.db_abs_path = db_abs_path
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        self.collection = {}
        self.selected_data = None

        self.industryList = pd.DataFrame(columns=["industry", "link"], index=None)
        self.loadIndustryListFromDB()

        self.stockList = pd.DataFrame(columns=["industry", "name", "symbol"], index=None)
        self.loadStockListFromDB()

        print(self.stockList)
        self.loadStocks()

    @property
    def industry_list(self):
        return self.industryList['industry'].tolist()

    def loadIndustryListFromDB(self, force_reload=False):
        self.industryList = pd.read_sql_query("SELECT * from industry", self.db_conn)
        if len(self.industryList.index) == 0 or force_reload:
            self.readIndustryList()
            self.industryList.sort_values(by='industry') 
            self.industryList.to_sql('industry', con=self.db_conn, if_exists='replace', index=False)

    def loadStockListFromDB(self, force_reload=False):
        self.stockList = pd.read_sql_query("SELECT * from stock", self.db_conn)
        
        if len(self.stockList.index) == 0 or force_reload:
            self.readStockList()
            self.stockList.drop_duplicates(subset=['symbol'], inplace=True)
            self.stockList.to_sql('stock', con=self.db_conn, if_exists='replace', index=False)
            

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
            self.m_hsIndexTotal.plot(x="times", y="closes", title="HS index", figsize=(10, 4))
            plt.title("HS index", fontproperties='SimHei', fontsize='large')
            plt.show()

    def readIndustryList(self):
        # clear industry list
        self.industryList.drop(self.industryList.index, inplace=True)

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
            self.industryList = self.industryList.append({"industry": child.get("title"), "link": link},
                                                             ignore_index=True)
        print("Created new industry list")

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
        for index, row in tqdm.tqdm(self.industryList.iterrows()):
            print("{}/{}: Getting {} information ({})".format(index, len(self.industryList), row["industry"],
                                                              row['link']))
            industry_url = row['link']
            browser.get(industry_url)
            # time.sleep(5)
            WebDriverWait(browser, timeout=10).until(LoadFinishCondition())  # , poll_frequency=5
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
                        # print("To next page")
                        WebDriverWait(browser, timeout=10).until(LoadFinishCondition())
                        html = browser.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                    else:
                        print("Cannot find button component!")
                        break
                else:
                    # print("Cannot find next page button!")
                    break
        browser.quit()
        print("Created new industry list")
        print(self.stockList.head(5))

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
            self.stockList = self.stockList.append(temp, ignore_index=True)

    def correctTimes(self):
        industries = self.stockList.groupby("industry")
        for name, industry in industries:
            filename = os.path.join("industries", "{}.csv".format(name))
            data = pd.read_csv(filename)
            data["times"] = ["{}.{}.{}".format(str(t)[:4], str(t)[4:6], str(t)[6:8]) for t in data["times"].tolist()]
            data.to_csv(filename)
        print(data.head(10))

    def loadStocks(self, threadNum=30):
        industries = self.stockList.groupby("industry")
        industryNames = list(industries.groups.keys())

        if len(industryNames) > 0:
            grouped = list(np.array_split(industryNames, threadNum))
            threads = list()

            mutex = Lock()
            for n in range(threadNum):
                threads.append(LoadThread(n, self, grouped[n], self.db_abs_path, mutex))
                threads[n].start()

            print("Waiting for reading stocks ...")
            for n in range(threadNum):
                threads[n].join()
        else:
            print("Already read all stocks ...")

    def getRandomStock(self):
        industries = self.stockList.groupby("industry")
        industryNames = list(industries.groups.keys())
        industryName = random.sample(industryNames, 1)[0]
        filename = os.path.join(self.localDir, "industries", "{}.csv".format(industryName))
        if os.path.exists(filename):
            data = pd.read_csv(filename)
            titles = list(data.columns)
            titles.remove("times")
            return data[["times", titles[0]]]
        else:
            print("Cannot find {} in industries directory".format(filename))
            return None


if __name__ == '__main__':
    stock = Stock()
