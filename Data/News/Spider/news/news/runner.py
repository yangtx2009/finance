from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from Data.News.Spider.news.news.spiders.SinaFinance import SinafinanceSpider
from Data.SqlClient import DatabaseClient


def runSpiders():
    process = CrawlerProcess()
    process.crawl(SinafinanceSpider)
    # process.crawl(MySpider2)
    process.start()


def displayResult():
    client = DatabaseClient()
    client.showAllTables()
    client.showTable("news")


if __name__ == '__main__':
    # runSpiders()
    displayResult()