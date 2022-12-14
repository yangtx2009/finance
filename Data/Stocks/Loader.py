import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
from datetime import datetime
import threading
import time
import requests
import matplotlib.pyplot as plt
import sys
import urllib.request
import urllib.error
import json
import gzip
import sqlite3 as sl


class LoadThread(threading.Thread):
    def __init__(self, id, stock, keyList, db_path, mutex):
        """
        @param id: thread id
        @param stock: stock class
        @param keyList
        """
        threading.Thread.__init__(self)

        self.id = id
        self.stock = stock
        self.keyList = keyList
        self.db_conn = sl.connect(db_path, check_same_thread=False)
        self.mutex = mutex

    def __del__(self):
        self.db_conn.close()

    def run(self):
        industries = self.stock.stockList.groupby("industry")

        for industry_name, data in industries:

            if not (industry_name in self.keyList):
                continue
            # print("------- {} -------".format(name))
            # in case the table does not exist
            # print(f'checking {industry_name}')
            # self.mutex.acquire()
            # try:
            #     self.db_conn.execute(f"""create table if not exists {industry_name} 
            #                         (times DATETIME,
            #                         PRIMARY KEY (times))""")
            #     stock_data = pd.read_sql_query(f"select * from {industry_name}", self.db_conn, index_col=None)
            # finally:
            #     self.mutex.release()
            stock_data = pd.DataFrame(columns=['times'], index=None)

            symbols = data["symbol"].tolist()
            stock_names = data["name"].tolist()

            for idx, symbol in enumerate(symbols):
                # if str(symbol).startswith('18'):
                stock_name = stock_names[idx]

                new_data = self.readStock(symbol, stock_name)
                if new_data is None:
                    continue

                # different stock has different length
                # add them from tail
                try:
                    new_data = new_data.rename(columns={'closes': stock_name})
                except ValueError:
                    print("check strange stock:", symbol, industry_name, stock_name)
                stock_data = pd.merge(stock_data, new_data, on="times", how='outer')

            stock_data = stock_data.sort_values(by=['times'])
            # remove the last day, because the stock values on the last day are usually wrong
            stock_data.drop(stock_data.tail(1).index, inplace=True)

            self.mutex.acquire()
            try:
                stock_data.to_sql(industry_name, con=self.db_conn, if_exists='replace', index=False)
            finally:
                self.mutex.release()

    def readStock(self, p_stockCode, stock_name, stockType=None, p_hs="hs", p_stockSplit="klinederc", p_period="day"):
        """
        :@param p_stockCode:
            深圳股票：+1
                0开头，002中小板，003主板，
                3创业板，
                B股：200
                新股：00
                080配股
            上海股票：+0
                6开头：主板
                B股：900
                新股：730
                配股：700
            4,8开头为新三板,普通用户无法交易4,8开头股票
        :@param stockType
        :@param p_hs: "hs",
        :@param p_stockSplit: "klinederc"/"kline"
        :@param p_period: "day"/"week"/"month"
        :@param p_draw
        :return:
        """
        fullCode = "{:06d}".format(int(p_stockCode))
        # try:
        if fullCode.startswith(('4','8')):
            return None
        elif fullCode.startswith(("6", "7", "9")):
            prefix = "0"
        else:
            prefix = "1"
        url = "http://img1.money.126.net/data/{}/{}/{}/times/{}{}.json".format(p_hs,
                                                                               p_stockSplit, p_period, prefix, fullCode)
        # print("URL:", url)
        try:
            response = requests.get(url, timeout=5)
            # response = urllib.request.urlopen(url, timeout=5)
        except requests.exceptions.Timeout:
            print(f"try get json again: {stock_name}")
            time.sleep(5)
            response = requests.get(url, timeout=10)
        finally:
            time.sleep(1)

        if response.status_code != 200:
            print(f'fail to reach {stock_name}: {url}')
            print("Http code: {}".format(response.status_code))
            return None

        json_data = response.json()  # utf-8

        # print("stock", l_jsonData["name"])
        data = pd.DataFrame(data={"times": json_data["times"], "closes": json_data["closes"]}, index=None)
        data['times'] = pd.to_datetime(data['times'], format='%Y%m%d')
        return data


class LoadFinishCondition:
    """
    https://blog.csdn.net/S_o_l_o_n/article/details/86644619
    """

    def __call__(self, driver):
        is_alert = bool(EC.alert_is_present()(driver))
        if is_alert:
            return True
        else:
            is_table_invisible = EC.invisibility_of_element_located((By.ID, 'table_wrapper-table'))(driver)
            is_table_visible = not bool(is_table_invisible)

            if is_table_visible:
                is_show_button_invisible = EC.invisibility_of_element_located((By.CLASS_NAME, "addzx"))(driver)
                is_show_button_visible = not bool(is_show_button_invisible)

                # print("elements", is_table_visible, is_show_button_visible)
                if is_show_button_visible:
                    time.sleep(1)
                    return True
                else:
                    return False
            else:
                return False
