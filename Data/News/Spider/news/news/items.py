# -*- coding: utf-8-*-
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    path = scrapy.Field()
    topic = scrapy.Field()
    content = scrapy.Field()


class DetailedNewsItem(scrapy.Item):
    ID = scrapy.Field()
    path = scrapy.Field()
    topic = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    comment_count = scrapy.Field()
