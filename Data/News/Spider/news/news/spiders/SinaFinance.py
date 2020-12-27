import scrapy
from scrapy.selector import Selector
from pprint import pprint
import sys
sys.path.append(r"D:\Projects\finance")
print(sys.path)

from Data.News.Spider.news.news.items import *


class SinafinanceSpider(scrapy.Spider):
    name = 'SinaFinance'
    allowed_domains = ['s.weibo.com/top/summary?cate=socialevent']
    start_urls = ['https://s.weibo.com/top/summary?cate=socialevent/']

    def parse(self, response, **kwargs):
        # blocks = response
        page = response.text
        page = page.replace("blk_macro", "")
        filtered = Selector(text=page)

        blocks = filtered.xpath('//div[starts-with(@data-sudaclick,"blk_")]')
        for block in blocks:
            blockSelector = Selector(text=block.get())
            header = blockSelector.xpath('//h2/a/text()').get()
            if header:
                # print(blockSelector.xpath('//li/a/text()'))
                item = NewsItem()
                item["path"] = blockSelector.xpath('//li/a/@href').get()
                item["content"] = blockSelector.xpath('//li/a/text()').get()
                item["topic"] = header
                if (item["path"] is None) or (item["content"] is None) or (item["topic"] is None):
                    continue
                yield item
