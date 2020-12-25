import scrapy
from scrapy.selector import Selector
from pprint import pprint


class BloombergSpider(scrapy.Spider):
    name = 'Bloomberg'
    allowed_domains = ['www.bloomberg.com/europe']
    start_urls = ['https://www.bloomberg.com/europe/']
    interesting_classes = ['story-package-module__story__headline-link',
                           'single-story-module__related-story-link',
                           'story-list-story__info__headline-link',
                           'single-story-module__headline-link']

    def parse(self, response, **kwargs):
        for interesting_class in self.interesting_classes:
            header = response.xpath('//a[@class="{}"]/text()'.format(interesting_class)).extract()
            header = [text.replace("\n", "").strip(" ") for text in header]
            pprint("header")
            pprint(header)