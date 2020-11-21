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

class LoadThread(threading.Thread):
    def __init__(self, id, stock, keyList):
        """
        @param id: thread id
        @param stock: stock class
        """
        threading.Thread.__init__(self)

        self.id = id
        self.stock = stock
        self.keyList = keyList
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        # print("Created thread {} ...".format(self.id))

    def run(self):
        industries = self.stock.m_stockList.groupby("industry")

        for name, industry in industries:
            if not (name in self.keyList):
                continue
            # print("------- {} -------".format(name))
            filename = os.path.join(self.localDir, "industries", "{}.csv".format(name))
            if os.path.exists(filename):
                d = datetime.fromtimestamp(os.path.getmtime(filename))
                now = datetime.now()
                delta = now - d
                days = delta.seconds // 360 // 24
                if days < 7:
                    self.stock.averaged[name] = pd.read_csv(filename)
                    continue

            symbols = industry["symbol"].tolist()
            merged = None
            for idx in range(len(symbols)):
                symbol = symbols[idx]
                newData = self.readStock(symbol, p_draw=False)
                if merged is None:
                    newData = newData.rename(columns={'closes': industry["name"].tolist()[idx]})
                    merged = newData
                else:
                    # different stock has different length
                    # add them from tail
                    newData = newData.rename(columns={'closes': industry["name"].tolist()[idx]})
                    merged = pd.merge(merged, newData, on="times", how='outer')

            merged["times"] = ["{}.{}.{}".format(str(t)[:4], str(t)[4:6], str(t)[6:8]) for t in merged["times"].tolist()]
            merged = merged.sort_values(by=['times'])
            merged.to_csv(filename, index=False)
            self.stock.averaged[name] = merged

    def readStock(self, p_stockCode, stockType=None, p_hs="hs", p_stockSplit="klinederc", p_period="day", p_draw=True):
        """
        :param p_stockCode:
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
        :param p_hs: "hs",
        :param p_stockSplit: "klinederc"/"kline"
        :param p_period: "day"/"week"/"month"
        :return:
        """
        fullCode = "{:06d}".format(int(p_stockCode))
        # try:
        if fullCode.startswith(("6","7","9")):
            prefix = "0"
        else:
            prefix = "1"
        url = "http://img1.money.126.net/data/{}/{}/{}/times/{}{}.json".format(p_hs,
                                                    p_stockSplit, p_period, prefix, fullCode)
        # print("URL:", url)
        l_jsonData = requests.get(url).json()
        # print("stock", l_jsonData["name"])
        data = pd.DataFrame(data={"times": l_jsonData["times"], "closes": l_jsonData["closes"]})

        if p_draw:
            data.plot(x="times", y="closes", figsize=(10, 4), grid=True)
            plt.title("{:} {:06d} {:}".format(l_jsonData["name"], int(p_stockCode), stockType), fontproperties='SimHei',
                      fontsize='large')
            plt.show()

        return data

class LoadFinishCondition:
    """
    https://blog.csdn.net/S_o_l_o_n/article/details/86644619
    """
    def __call__(self, driver):
        is_alert=bool(EC.alert_is_present()(driver))
        if is_alert:
            return True
        else:
            is_table_invisible=EC.invisibility_of_element_located((By.ID,'table_wrapper-table'))(driver)
            is_table_visible = not bool(is_table_invisible)

            if is_table_visible:
                is_show_button_invisible = EC.invisibility_of_element_located((By.CLASS_NAME, "addzx"))(driver)
                is_show_button_visible = not bool(is_show_button_invisible)

                print("elements", is_table_visible, is_show_button_visible)
                if is_show_button_visible:
                    time.sleep(1)
                    return True
                else:
                    return False
            else:
                return False