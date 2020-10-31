from bs4 import BeautifulSoup
import requests
import json
import js2py
import time
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import threadpool

code_list = []
actions = []
time_ms = int(round(time.time() * 1000))
# 获取基金代码和名称
def  getJJCode_Name(page=1):
    url = "http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=1&lx=1&letter=&gsid=&text=&sort=zdf,desc&page=" \
          + str(page) + ",200&dt=1562661541203&atfc=&onlySale=0"
    js_var = requests.get(url).text
    db = js2py.eval_js(js_var)
    pages = db['pages']
    curpage = db['curpage']
    datas = db['datas']
    for data in datas:
        print(data[0] + '  ' + data[1])
        code_list.append(data[0])
        action =fund_breif(data[0])
        actions.append(action)
    helpers.bulk(es, actions)
    actions.clear()
    print('current page --->' + curpage)

    if int(pages) > int(curpage):
        getJJCode_Name(int(curpage) + 1)


# 获取基金概况
def fund_breif(code):
    url = "http://fundf10.eastmoney.com/jbgk_" + code + ".html"
    html = requests.get(url)
    html.encoding = 'utf-8'
    currentPage = BeautifulSoup(html.text, 'lxml')

    jj_table = currentPage.find('table', {'class': 'info'})
    row_1 = jj_table.find('tr')

    row_1_td_1 = row_1.find('td')
    row_1_td_2 = row_1_td_1.find_next('td')

    print(row_1_td_1.get_text() + " " + row_1_td_2.get_text())

    row_2 = row_1.next_sibling
    row_2_td_1 = row_2.find('td')
    row_2_td_2 = row_2_td_1.find_next('td')

    print(row_2_td_1.get_text() + " " + row_2_td_2.get_text())

    row_3 = row_2.next_sibling
    row_3_td_1 = row_3.find('td')
    row_3_td_2 = row_3_td_1.find_next('td')
    print(row_3_td_1.get_text() + " " + row_3_td_2.get_text())

    row_4 = row_3.next_sibling
    row_4_td_1 = row_4.find('td')
    row_4_td_2 = row_4_td_1.find_next('td')
    print(row_4_td_1.get_text() + " " + row_4_td_2.get_text())

    row_5 = row_4.next_sibling
    row_5_td_1 = row_5.find('td')
    row_5_td_2 = row_5_td_1.find_next('td')
    print(row_5_td_1.get_text() + " " + row_5_td_2.get_text())

    action = {
        "_index": "fund_breif",
        "_type": "_doc",
        "_source": {
            "fund_full_name": row_1_td_1.get_text(),
            'fund_name': row_1_td_2.get_text(),
             'fund_code': code,
            "fund_type": row_2_td_2.get_text(),
             "issue_date": row_3_td_1.get_text(),
             "establish_date": row_3_td_2.get_text(),
            "aum": row_4_td_1.get_text(),
            "share_size": row_4_td_2.get_text(),
            "company": row_5_td_1.get_text()
            }
        }
    return action


# 获取净值
def net_value(code, curr_page=1):
    url = "http://api.fund.eastmoney.com/f10/lsjz?callback=fun&fundCode=000209&pageIndex="\
          + str(curr_page) + "&pageSize=200&startDate=&endDate=&_="+ str(time_ms)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
        'Cookie': 'st_pvi=01936466598903; st_sp=2019-07-02%2020%3A04%3A13; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink',
        'Referer': 'http://fundf10.eastmoney.com/jjjz_' + code + '.html'
    }

    v_actions = []
    js_var = requests.get(url, headers=headers).text
    mes = json.loads(js_var[4:-1])
    for d in mes['Data']['LSJZList']:
        danweijingzhi = 0
        lishijingzhi = 0
        zengzhanglv = 0
        if d['DWJZ'].isdecimal() :
            danweijingzhi = float(d['DWJZ'])
        if d['LJJZ'].isdecimal() :
            lishijingzhi = float(d['LJJZ'])
        if d['JZZZL'].isdecimal():
            print("d = " + d['JZZZL'])
            print(d['JZZZL'].isspace())
            zengzhanglv = float(d['JZZZL'])

        action = {
            "_index": "fund_netvalue",
            "_type": "_doc",
            "_source": {
                "code" : code,
                "date" : d['FSRQ'],
                "danweijingzhi": danweijingzhi,
                "lishijingzhi": lishijingzhi,
                "zengzhanglv": zengzhanglv
            }
        }
        v_actions.append(action)
    helpers.bulk(es, v_actions)

    print('current page --->' + str(mes['PageIndex']))

    if int(mes['TotalCount']) > int(mes['PageSize'])* int(mes['PageIndex']) :
        c_page = int(mes['PageIndex']) + 1
        net_value(code, c_page)


def netvalue_threadpool():
    pool = threadpool.ThreadPool(10)
    t_reqs = threadpool.makeRequests(net_value, code_list)
    [pool.putRequest(req) for req in t_reqs]
    pool.wait()

if __name__ == '__main__':
    es = Elasticsearch([{"host": "192.168.31.213", "port": 9200}])
    # getJJCode_Name()
    netvalue_threadpool()

    # net_value("001195", curr_page=1)