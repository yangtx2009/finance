"""
https://www.jianshu.com/p/1f4a708bf76a
"""
import scrapy
from pprint import pprint
import sys
import os
sys.path.append(os.path.abspath('../../../..'))
import re

import json
from Data.News.Spider.news.news.items import *
import Data.News.Spider.news.news.pipelines as pipelines


class SinaSpider(scrapy.Spider):
    name = 'Sina'
    custom_settings = {
        'ITEM_PIPELINES': {
            'news.pipelines.DetailedNewsPipeline': 400
        }
    }

    def start_requests(self):
        top_form = 'http://interface.sina.cn/ent/feed.d.json?ch={0}&col={0}&show_num=20&page={1}'
        public_form = 'http://interface.sina.cn/wap_api/layout_col.d.json?col={0}&level=1&show_num=30&page={1}'
        code_map = {'international': '56261', 'domestic': '56262', 'society': '56264'}
        max_page = 5

        for topic in ['international', 'domestic', 'society']:
            for i in range(max_page):
                url = public_form.format(code_map[topic], i + 1)
                yield scrapy.FormRequest(url)

    def parse(self, response):
        try:
            raw_data = json.loads(response.text.replace("\\\"", " ").encode('ascii').decode('unicode-escape'))['result']['data']
        except Exception as e:
            print("error exists", e)
            return

        count = raw_data['count']
        data = raw_data['list']
        print('count:', count)

        for msg_dict in data:
            item = DetailedNewsItem()
            item['ID'] = msg_dict['_id']
            item['path'] = msg_dict['URL']
            item['content'] = msg_dict['title']
            item['time'] = msg_dict['cdateTime']
            item['comment_count'] = msg_dict['comment']

            commentid = msg_dict['commentid']
            if commentid.startswith('gn'):
                item['topic'] = 'domestic'
            elif commentid.startswith('gj'):
                item['topic'] = 'international'
            elif commentid.startswith('sh'):
                item['topic'] = 'society'
            else:
                item['topic'] = 'none'
            yield item
