from fond import Fond
import re
import os
import pandas as pd
import pprint
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from matplotlib.font_manager import _rebuild
import numpy as np
from urllib import request
from urllib import parse
import json

class Dataset:
    def __init__(self):
        self.fonds = None
        self.getFondList()

    def getFondList(self):
        if os.path.exists("fond_names.csv"):
            self.fonds = pd.read_csv("fond_names.csv")
        else:
            # 获取所有基金名称及代码
            page = self.getData("http://fund.eastmoney.com/js/fundcode_search.js")
            page = page.replace("var r = ", "")
            page = page.replace(";", "")[2:][:-1]
            page = page.replace("\"", "")
            fonds = page.split("],[")

            for idx, fond in enumerate(fonds):
                fonds[idx] = fond.replace("[", "").replace("]", "").split(",")
            self.fonds = pd.DataFrame(fonds)
            self.fonds.to_csv("fond_names.csv")
        print(self.fonds)
        print("\n\n")

    def getData(self, url):
        req = request.Request(url)  # POST方法
        page = request.urlopen(req).read().decode("utf-8")
        return page

    def get_stock(self):
        # https://zhuanlan.zhihu.com/p/33145465
        pass

    def getFond(self, id="001195"):
        page = self.getData("http://fund.eastmoney.com/pingzhongdata/{}.js?v=20160518155842".format(id))
        print("\n".join(page.split(";")))
        fond = Fond(page)
        fond.plotWorthTrend()

        print("\n\n")
        # real-time details
        page = self.getData("http://fundgz.1234567.com.cn/js/{}.js?rt=1463558676006".format(id))
        page = page.replace("jsonpgz(", "")
        page = page.replace(");", "")

        page = json.loads(page)
        pprint.pprint("real-time details: {}\n{}".format(id, page))

if __name__ == '__main__':
    dataset = Dataset()
    dataset.getFond()