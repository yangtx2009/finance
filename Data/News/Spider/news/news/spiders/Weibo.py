import scrapy
from scrapy.selector import Selector


class WeiboSpider(scrapy.Spider):
    name = 'Weibo'
    allowed_domains = ['s.weibo.com']
    start_urls = ['https://s.weibo.com/top/summary?cate=socialevent',
                  'https://s.weibo.com/top/summary?cate=realtimehot']

    def parse(self, response):
        page = response.text
        filtered = Selector(text=page)
        header = filtered.xpath('//td[@class="td-02"]/a/text()').extract()
        print(header)