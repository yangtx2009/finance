# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from Data.SqlClient import DatabaseClient
from Data.News.Spider.news.news.items import NewsItem


class NewsPipeline(object):
    def __init__(self):
        print("NewsPipeline")
        self.client = DatabaseClient()
        if not self.client.tableExist("news"):
            self.client.createTable("news", ["path VARCHAR(255)", "topic VARCHAR(255)", "content VARCHAR(255)"], "path")

    def process_item(self, item, spider):
        if spider.name in ['SinaFinance']:
            path = item["path"]
            topic = item["topic"]
            content = item["content"]
            self.client.insertData("news", {"path": path, "topic": topic, "content": content})    #
            return item

    def close_spider(self, spider):
        self.client.disconnect()


class DetailedNewsPipeline(object):
    def __init__(self):
        print("DetailedNewsPipeline")
        self.client = DatabaseClient()
        if not self.client.tableExist("detailed_news"):
            self.client.createTable("detailed_news",
                                    ["ID VARCHAR(255)", "time VARCHAR(255)", "path VARCHAR(255)",
                                     "topic VARCHAR(255)", "content VARCHAR(255)",
                                     "comment_count INT"],
                                    "ID")

    def process_item(self, item, spider):
        if spider.name in ['Sina']:
            ID = item["ID"]
            time = item["time"]
            path = item["path"]
            topic = item["topic"]
            content = item["content"]
            comment_count = item["comment_count"]
            self.client.insertData("detailed_news", {"ID": ID, "time": time, "path": path, "topic": topic,
                                                     "content": content, "comment_count": comment_count}, "ID")
            return item

    def close_spider(self, spider):
        self.client.disconnect()


if __name__ == '__main__':
    pipline = NewsPipeline()
