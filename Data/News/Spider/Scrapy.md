# Scrapy

## 操作

* 新建爬虫项目

  ```
  scrapy startproject --logfile="./logfile.log" project_name
  ```

* 运行单个爬虫文件

  ```python
  scrapy runspider --loglevel=INFO xxx.py
  ```

* 查看配置信息

  ```python
  scrapy settings --get XXX
  ```

  * BOT_NAME: 爬虫机器人名
  * SPIDER_MODULES: 爬虫模块位置

* 通过shell命令可以启动Scrapy的交互终端

  ```python
  scrapy shell http://www.baidu.com --nolog
  response.xpath("/html/head/title")
  exit()
  ```

* 用浏览器查看网页

  ```python
  scrapy view http://www.baidu.com
  ```

* 查看硬件性能

  ```python
  scrapy bench
  ```

* 快速生成爬虫文件

  ```python
  scrapy genspider -l # 查看爬虫模板
  scrapy genspider -d csvfeed
  scrapy genspider -t basic weisuen iqianyue.com # 生成一个名为WeisuenSpider的爬虫类
  ```

* 启动爬虫

  ```python
  scrapy crawl weisuen --loglevel=INFO
  scrapy crawl weisuen -a p_url=http:://www.baidu.com --loglevel=INFO	# 通过-a进行传参
  ```

* 列出所有爬虫

  ```python
  scrapy list
  ```

## Items

Item对象是用来保存爬取的数据的容器，它被定义在items.py。对数据结构化可以用通过Field。

```python
class ScraperItem(scrapy.Item):
	urlname=scrapy.Field()
	...
```
存储具体数据的时候，只需要实例化该类。

```python
data = ScraperItem(urlname="http://www.baidu.com")
print(data)	# 输出为dict
data["urlname"] # 像dict一样调用attribute
data.keys()
data.items()	# 获取项目视图ItemsView
```

## XPath

* `//p`: 获取所有`<p>`标签的数据

* `//Z[@X=”Y”]`获取所有属性X的值为Y的`<Z>`标签内容，如

  ```
  //img[@class="f1"]
  ```

## Spider

必要的attribute

* name: 爬虫名

* allowed_domains: 允许爬行的域名。如果启动了OffsiteMiddleware，非允许的域名对应的网址则会自动过滤

* start_urls: 爬行的起始网址

* parse(): 处理Scrapy爬虫爬行到的网页响应（response，也就是返回的数据或网页）的默认方法，通过该方法，可以对响应进行处理并返回处理后的数据，同时该方法也负责链接的跟进

  ```python
  def parse(self, response):
  	item=ScraperItem()
  	item['urlname'] = response.xpath("/html/head/title/text()")
  ```

* start_requests(): 如果不想用start_urls作为起始网址，可以用过重写该方法定义如何开始爬行

### XMLFeedSpider

专门用来处理XML文件的Spider类型。它比Basic类型Spider要多以下特征:

* iterator: 设置的是使用哪个迭代器，'iternodes'（默认），’html’或’xml'
* itertag: 设置开始迭代的节点
* parse_node(self, response, selector): 在节点与所提供的标签名相符合的时候会被调用，在该方法中，可以进行一些信息的提取和处理的操作。
* namespaces
* adapt_response(response): 分析相应
* process_results(response, result): Spider返回结果时被调用，主要对结果进行后处理

### CSVFeedSpider

专门用来处理CSV文件的Spider类型。它比Basic类型Spider要多以下特征:

* headers: 处理某几列数据
* delimiter: 存放字段之间的间隔符
* parse_row(response, row): 用来接收一个response对象，并处理某一行数据，它会针对每一行数据被反复调用

## 批量运行爬虫

批量运行爬虫程序可以通过以下两种方式

* CrawProcess
* 重写crawl命令

获取所有的爬虫文件

```python
crawler_process.spider_loader.list()
```

## 处理反爬虫机制

* 禁止Cookie

  settings.py中设置COOKIES_ENABLED = False

* 设置下载延时

  settings.py中设置DOWNLOAD_DELAY = 0.7

* 使用IP池

  如果IP被封禁了，就需要更换IP。获取多个代理服务器，将这些代理服务器的IP组成一个IP池，爬虫每次对网页进行爬取的时候，可以随机选择IP池中的一个IP进行。为此需要在middlewares.py中建立一个下载中间件HttpProxyMiddleware用来定义IP选择规则。在settings.py中，其中设置IP池: IPPOOL。

* 使用用户代理池

  User-Agent。基于修改用户信息如浏览器，客户端类型。使用UserAgentMiddleware

* 分布式爬取

  scrapinghub

