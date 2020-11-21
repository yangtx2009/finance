import re
import os
import pandas as pd
import pprint
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import time
import pytz
import datetime
import matplotlib.pyplot as plt
from matplotlib.font_manager import _rebuild
import numpy as np

class Fond:
    def __init__(self, data_str):
        self.data_str = data_str
        self.data = {"fS_name": "基金名称",
                     "fund_sourceRate": "原费率",
                     "fund_Rate": "现费率",
                     "fund_minsg": "最小申购金额",
                     "stockCodes": "基金持仓股票代码",
                     "syl_1n": "近1年收益率",
                     "syl_6y": "近6月收益率",
                     "syl_3y": "近3月收益率",
                     "syl_1y": "近1月收益率",
                     # "Data_netWorthTrend":"单位净值走势",
                     "Data_ACWorthTrend": "累计净值走势",
                     "equityReturn": "净值回报",
                     # "unitMoney":"每份派送金",
                     "Data_grandTotal": "累计收益率走势",
                     "swithSameType1m": "近1月同类型基金",
                     "swithSameType3m": "近3月同类型基金",
                     "swithSameType1y": "近1年同类型基金",
                     "swithSameType3y": "近3年同类型基金",
                     }

        self.fS_name = data_str.split("fS_name")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" ")
        self.fund_sourceRate = float(
            data_str.split("fund_sourceRate")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" "))
        self.fund_Rate = float(
            data_str.split("fund_Rate")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" "))
        self.fund_minsg = int(
            data_str.split("fund_minsg")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" "))
        self.stockCodes = data_str.split("stockCodes")[1].split(";")[0].replace("\"", ""). \
            replace("=", "").replace("[", "").replace("]", "").strip(" ").split(",")
        self.syl_1n = float(data_str.split("syl_1n")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" "))
        self.syl_6y = float(data_str.split("syl_6y")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" "))
        self.syl_3y = float(data_str.split("syl_3y")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" "))
        self.syl_1y = float(data_str.split("syl_1y")[1].split(";")[0].replace("\"", "").replace("=", "").strip(" "))
        self.swithSameType1m = None
        self.swithSameType3m = None
        self.swithSameType6m = None
        self.swithSameType1y = None
        self.swithSameType3y = None

        self.unitMoney_times = []
        # self.Data_netWorthTrend = []
        self.equityReturn = []
        self.unitMoney = []
        self.Data_grandTotal = []

        self.ACWorthTrend_times = []
        self.Data_ACWorthTrend = []

        self.getSameType()
        self.getWorthTrend()
        self.getAcWorthTrend()

        for key, value in self.data.items():
            print("{}:\n {}".format(value, getattr(self, key)))
        # self.var_strs = data_str.split(";")

    def getSameType(self):
        temp = self.data_str.split("swithSameType")[1].split(";")[0].replace("\'", "").replace("=", "").strip(" ")[1:-1]
        # print(temp)
        p1 = re.compile(r'[[](.*?)[]]', re.S)
        rows = re.findall(p1, temp)
        # pprint.pprint(rows)

        dataFrame = pd.DataFrame(columns=["ID", "name", "rate"])
        for item in rows[0].split(","):
            dataFrame = dataFrame.append(
                {"ID": item.split("_")[0], "name": item.split("_")[1], "rate": float(item.split("_")[2])},
                ignore_index=True)
        self.swithSameType1m = dataFrame

        dataFrame = pd.DataFrame(columns=["ID", "name", "rate"])
        for item in rows[1].split(","):
            dataFrame = dataFrame.append(
                {"ID": item.split("_")[0], "name": item.split("_")[1], "rate": float(item.split("_")[2])},
                ignore_index=True)
        self.swithSameType3m = dataFrame

        dataFrame = pd.DataFrame(columns=["ID", "name", "rate"])
        for item in rows[2].split(","):
            dataFrame = dataFrame.append(
                {"ID": item.split("_")[0], "name": item.split("_")[1], "rate": float(item.split("_")[2])},
                ignore_index=True)
        self.swithSameType6m = dataFrame

        dataFrame = pd.DataFrame(columns=["ID", "name", "rate"])
        for item in rows[3].split(","):
            dataFrame = dataFrame.append(
                {"ID": item.split("_")[0], "name": item.split("_")[1], "rate": float(item.split("_")[2])},
                ignore_index=True)
        self.swithSameType1y = dataFrame

        dataFrame = pd.DataFrame(columns=["ID", "name", "rate"])
        for item in rows[4].split(","):
            dataFrame = dataFrame.append(
                {"ID": item.split("_")[0], "name": item.split("_")[1], "rate": float(item.split("_")[2])},
                ignore_index=True)
        self.swithSameType3y = dataFrame

    def getWorthTrend(self):
        temp = self.data_str.split("Data_netWorthTrend")[1].split(";")[0]
        p1 = re.compile(r'[{](.*?)[}]', re.S)
        rows = re.findall(p1, temp)
        for row in rows:
            items = row.split(",")
            for idx, item in enumerate(items):
                if idx == 0:
                    self.unitMoney_times.append(int(item.split(":")[1]))
                elif idx == 1:
                    self.unitMoney.append(float(item.split(":")[1]))
                elif idx == 2:
                    self.equityReturn.append(float(item.split(":")[1]))

    def getAcWorthTrend(self):
        temp = self.data_str.split("Data_ACWorthTrend")[1].split(";")[0].replace("=", "").strip()[1:-1]
        p1 = re.compile(r'[[](.*?)[]]', re.S)
        rows = re.findall(p1, temp)
        for row in rows:
            items = row.split(",")
            for idx, item in enumerate(items):
                if idx == 0:
                    self.ACWorthTrend_times.append(int(item))
                elif idx == 1:
                    self.Data_ACWorthTrend.append(float(item))

    def secondsToChineseTime(self, milliseconds=1432828800000):
        seconds = milliseconds // 1000
        ltime = time.gmtime(seconds)
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
        # print("UTC", timeStr)
        tzinfo = pytz.timezone('Asia/Shanghai')
        # datetime.timezone.utc
        datetime_obj = datetime.datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
        datetime_obj_utc = datetime_obj.astimezone(tzinfo).strftime('%Y-%m-%d %H:%M:%S.%f')

        # print("Asia/Shanghai", datetime_obj_utc)
        return datetime_obj_utc

    def plotWorthTrend(self):
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(np.arange(0, len(self.unitMoney)), self.unitMoney)
        ax.plot(len(self.unitMoney), self.unitMoney[-1], "ro")
        ax.text(x=len(self.unitMoney) - 100, y=self.unitMoney[-1] + 0.05,
                s="{} {}".format(self.secondsToChineseTime(self.unitMoney_times[-1])[:-16], self.unitMoney[-1]))

        ax.set_xlim(-10, len(self.unitMoney) + 10)
        # plt.xticks(np.arange(0, len(self.unitMoney), 100))
        # print(ax.get_xticks().tolist())
        ax_list = ax.get_xticks().tolist()[:-1]
        # print("ax_list", ax_list, len(self.times), len(self.unitMoney))
        xlabels = [self.secondsToChineseTime(self.unitMoney_times[int(idx)])[:-16] for idx in ax_list]
        ax.set_xticklabels(xlabels)
        ax.set_yticks(np.arange(np.min(self.unitMoney) - 0.1, np.max(self.unitMoney) + 0.1, 0.1))

        plt.grid()
        plt.title(self.fS_name, fontproperties='SimHei', fontsize='large')
        plt.tight_layout()
        plt.show()