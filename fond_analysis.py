#coding:utf-8
"""
基金实时信息：http://fundgz.1234567.com.cn/js/001186.js?rt=1463558676006

001186为基金代号

返回值：jsonpgz({"fundcode":"001186","name":"富国文体健康股票","jzrq":"2016-05-17","dwjz":"0.7420","gsz":"0.7251","gszzl":"-2.28","gztime":"2016-05-18 15:00"});

基金详细信息：http://fund.eastmoney.com/pingzhongdata/001186.js?v=20160518155842

http://fund.eastmoney.com/js/fundcode_search.js
所有基金名称列表代码

http://fund.eastmoney.com/js/jjjz_gs.js?dt=1463791574015
所有基金公司名称列表代码
"""

from urllib import request
from urllib import parse
import json
import re
import os
import pandas as pd
import pprint
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from matplotlib.font_manager import _rebuild
import numpy as np
from fond import Fond

# from bs4 import BeautifulSoup
themes = {
    "virus_provention": ["161726", "501009", "501010", "161122", "110023"],
    "social_security": ["002408", "003095", "003096", "005453", "005454"],
    "biomedical": ["161726", "501009", "501010", "161122", "110023", "161706"],
    "medical_equipment": ["006981", "007005", "162412", "502056", "160219", "001550", "003284", "000059", "006569", "001344", "007883", "002919"],
    "pork": ["005106", "003751", "290014", "290002", "001027", "000598", "001195", "217005", "110005", "519019"],
}

def main():
    #print(fond.__dict__)
    pass

if __name__ == '__main__':
    _rebuild()
    main()
