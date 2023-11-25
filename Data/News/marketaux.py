"""
https://www.marketaux.com/account/dashboard
"""
import requests
import urllib
from datetime import datetime, timedelta
import json

from base_news_api import BaseNewsApi

class MarketAuxApi(BaseNewsApi):
    def __init__(self):
        super().__init__()
        self.token = self._read_token("marketaux")
        self.base_url = self._read_base_url("marketaux")
        print(self.base_url)

    def get_latest_news(self, industries=[], published_after=None, limit=10):
        request_url = self.base_url+"/v1/news/all"
        print("request_url:", request_url)

        params = {"api_token": self.token,
                  "language": "en",
                  "filter_entities": "true"}
        
        if isinstance(industries, str):
            params["industries"] = industries
        elif isinstance(industries, list) and len(industries) > 0:
            params["industries"] = ",".join(industries)

        if limit > 0:
            params["limit"] = limit

        if published_after is not None:
            if isinstance(published_after, str):
                params["published_after"] = published_after
            elif isinstance(published_after, datetime):
                params["published_after"] = published_after.strftime("%Y-%m-%dT%H:%M")

        response = requests.get(request_url, params=params)
        if response.ok:
            print(json.dumps(response.json()))
        else:
            print(response.request.url)
            print(response.status_code)


if __name__ == '__main__':
    api = MarketAuxApi()
    api.get_latest_news(industries="Technology", 
                        published_after=datetime.now()+timedelta(days=-7),
                        limit=10)