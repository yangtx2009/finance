# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from Data.SqlClient import DatabaseClient
from Data.News.news.news.items import NewsItem


class NewsPipeline:
    def __init__(self):
        print("NewsPipeline")
        self.client = DatabaseClient()
        if not self.client.tableExist("news"):
            self.client.createTable("news", ["path VARCHAR(255)", "topic VARCHAR(255)", "content VARCHAR(255)"], "path")

    def process_item(self, item, spider):
        path = item["path"]
        topic = item["topic"]
        content = item["content"]
        self.client.insertData("news", {"path": path, "topic": topic, "content": content})    #
        return item

    def close_spider(self, spider):
        self.client.disconnect()


if __name__ == '__main__':
    pipline = NewsPipeline()
