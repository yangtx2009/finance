# Scrapy settings for news project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'news'

SPIDER_MODULES = ['news.spiders']
NEWSPIDER_MODULE = 'news.spiders'


# Crawl responsibly by identifying yourself (and your website)s on the user-agent
# USER_AGENT = 'news (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   'authority': 'scrapeme.live',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
   'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
   'Accept-Encoding': 'gzip,deflate,br',
   #'Connection': "keep-alive",
   'Content-Type': 'application/json',
   'Cache-Control': "max-age=0",
   'dnt': '1',
   'sec-fetch-site': 'none',
   'sec-fetch-mode': 'navigate',
   'sec-fetch-user': '?1',
   'sec-fetch-dest': 'document',
   #'Cookie': "_reg-csrf=s%3Aqj_FkWA0I7JJAV-0C1oG6hRc.Fc0bGkiLUpXAHzEIu5boPkSN6HDPsDNNGrzuXN02Roo; _reg-csrf-token=85yAKUsP-abYVCc7htm7y7AtSaeEkNhkFU-4; agent_id=2cfa0570-0a22-4ff8-a451-49d9831708f2; session_id=9aeb6afc-9998-4da9-8176-a5c568c9b55b; session_key=2abe7a6a86ff2a0d3bce83cb75dbb7224ebcdf4f; _user-status=anonymous; _sp_krux=true; _sp_v1_uid=1:83:47a62c40-bb78-44f3-8a5a-84167572eb4c; _sp_v1_data=2:265834:1607801170:0:21:0:21:0:0:_:-1; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKxs_IAzEMamN1YpRSQcy80pwcILsErKC6lpoSSjq…5b7c6da336d3c76a6668588e0ad0f327d34193dab63a16ff517c51528a:Yupw+2xUETZ6LJTprsmCr6pPSJ1hU8jKKdcyiFyWUApDbbpwX3DBMhzuXvQNhtQFghON7owx/oII0GpVDS2s9w==:1000:2HujSHlu/X1oqiGmjNIinGVQaP/e0OotrF2m3Ll/qp3ktxKD4vOGIcov0j2lsm6VURSzA1KT6J7iUpwxvAnLY7yYD22oQwBaZIu3Sa5qTLVzX3TxXf6lEasIdb/+dmnM8teN0+WgrXyoVnjkEAyGvxwPEAJs4nZCxvDiZLbkCmA=; outbrain_cid_fetch=true; _user_newsletters=[]; _uetsid=e66360a03caf11eb933b514cbcd4eca3; _uetvid=e6634e803caf11ebad432760d35ecf87; _dc_gtm_UA-11413116-1=1; _pxff_cc=U2FtZVNpdGU9TGF4Ow=="
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'news.middlewares.NewsSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'news.middlewares.NewsDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'news.pipelines.NewsPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
