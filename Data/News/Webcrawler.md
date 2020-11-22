# Web Crawler 网络爬虫

读书笔记

## 分类

* General Purpose Web Crawler 通用网络爬虫
* **Focuses Web Crawler 聚焦网络爬虫**
* Incremental Web Crawler 增量式网络爬虫
* Deep Web Crawler 深层网络爬虫

## 步骤

1. 定义和描述爬取目标
2. 获取初始URL
3. 根据初始的URL爬取页面，并获得新的URL
4. 从新的URL中过滤掉与爬取目标无关的链接。因为聚焦网络爬虫对网页的爬取是有目的性的，所以与目标无关的网页将会被过滤掉。同时，也需要将已爬取的URL地址存放到一个URL列表中，用于去重和判断爬取的进程。
5. 将过滤后的链接放到URL队列中
6. 从URL队列中，根据搜索算法，确定URL的优先级，并确定下一步要爬取的URL地址

## 爬行策略

* 深度优先爬行策略
* 广度优先爬行策略
* 大站优先策略(网页数量多的某网站)
* 反链策略(该网页被其他网页指向的次数, 代表着该网页被其他网页的推荐次数)
* OPIC策略
* Partial PageRank策略

## 网页更新策略

网站的更新频率与爬虫访问网站的频率越接近，则效果越好

* ~~用户体验策略~~(只针对于搜索引擎)
* 历史更新数据策略: 泊松过程建模
* 聚类分析策略

## 网页分析算法

* ~~基于用户行为~~(只针对于搜索引擎)
* 基于网络拓扑: 分析网页的链接关系、结构关系、已知网页或数据
  * 基于网页粒度
    * PageRank算法: 根据网页之间的链接关系对网页的权重进行计算
    * HITS算法
  * 基于网页块粒度: 对一个网页中的外部链接划分层次，不同层次的外部链接对于该网页来说，其重要程度不同
  * 基于网站粒度
    * SiteRank算法
* 基于网页内容

## 身份识别

* 通过HTTP请求中的User Agent字段告知自己的身份信息
* 根据站点下的Robots.txt文件来确定可爬取的网页范围(Robots协议)

## Urllib总结

* file = urllib.request.urlopen(url, timeout=sec) 打开连接
* urllib.request.urlretrieve 打开连接并保存
* urllib.request.urlcleanup 清除缓存
* file.info() 返回与当前环境有关的信息
* fle.getcode() 返回状态码
* file.geturl() 返回地址
* urllib.request.quote 对不符合标准的字符串编码
* **urllib.request.unquote 对URL的字符串解码**
* 应对403错误(必须伪装成浏览器才能访问): 
  * urllib.request.build_opener()
  * req.add_header(headers)

```python
headers=("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) ...")
opener = urllib.request.build_opener()
opener.addheaders = [headers]
data = opener.open(url).read()
```

or

```python
req = urllib.request.Request(url)
req.add_header("User-Agent", "...")
```

* urllib.request.HTTPHandler(debuglevel=1) & urllib.request.HTTPSHandler(debuglevel=1) 打印调试日志
* urllib.error.URLError & urllib.error.HTTPError + try...except... 处理异常
  * 连接不上服务器
  * 远程URL不存在
  * 无网络
  * ...

