"""
pip install newscatcherapi
"""

import requests
import urllib
from datetime import datetime, timedelta
import json
import pathlib

from newscatcherapi import NewsCatcherApiClient

from base_news_api import BaseNewsApi

class NewsCatcherApi(BaseNewsApi):
    def __init__(self):
        super().__init__()
        self.token = self._read_token("newscatcher")
        self.newscatcherapi = NewsCatcherApiClient(x_api_key=self.token)
        self.current_dir = pathlib.Path(__file__).parent.resolve()
        print(self.current_dir)

    def search(self, query, from_, to_, limit=10, countries="US"):
        if isinstance(from_, datetime):
            from_ = from_.strftime("%Y/%m/%d")
        if isinstance(to_, datetime):
            to_ = to_.strftime("%Y/%m/%d")

        response = self.newscatcherapi.get_search(q=query,
                                         lang='en',
                                         from_=from_, to_=to_,
                                         countries=countries,
                                         page_size=limit)
        # print(json.dumps(response))

        with open(self.current_dir / "data1.json",'w') as fi:
            json.dump(response,fi, indent=4)
        
    def get_latest_news(self, topic, when="1h", limit=10, countries="US"):
        if topic not in ['news', 'sport', 'tech', 'world', 
                      'finance', 'politics', 'business', 
                      'economics', 'entertainment', 
                      'beauty', 'travel', 'music', 
                      'food', 'science', 'gaming', 'energy']:
            raise Exception("invalid topic")

        response = self.newscatcherapi.get_latest_headlines(lang='en',
            countries=countries,
            topic=topic,
            when=when,
            page_size=limit)
        # print(json.dumps(response))

        with open(self.current_dir / "data2.json",'w') as fi:
            json.dump(response,fi, indent=4)

if __name__ == '__main__':
    api = NewsCatcherApi()
    api.get_latest_news(topic="tech",
                        limit=10)