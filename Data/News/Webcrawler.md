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

## RegEx总结

### 原子

匹配的基本单位是原子（character），可以是一个字母，数字或任何字符

* 单个原子可以是以下可能
  * 字符本身或\n，\t
  * \w 匹配任意字母，数字或下划线
  * \W 匹配除字母，数字或下划线以外的任意一个字符
  * \d 匹配任意一个十进制数
  * \D 匹配除十进制数以外的任意一个字符
  * \s 匹配任意一个空白字符
  * \S 匹配除空白字符以外的任意一个字符

如匹配"67python8"

```python
\w\dpython\w
```

* 也可以是一组地位平等的原子（原子表）
  * [xyz] 表示xyz中任意一个字符
  * [^xyz] 表示除xyz以外的任意一个字符

### 元字符（metacharacters）

* .  匹配除换行符以外的任意一个字符，如".python..."匹配"5python_pz"
* ^ 匹配字符串的开始位置，如"^abd"匹配"abdfv53"
* $ 匹配字符串的结束位置，如"53\$"匹配"abdfv53"
* \* 匹配0次，1次或多次前面的原子，如"py.\*n"匹配"python"
* ? 匹配0次或1次前面的原子
* \+ 匹配1次或多次前面的原子
* {n} 前面的原子恰好出现n次，如"cd{2}"匹配"cdd"
* {n,} 前面的原子至少出现n次
* {n,m} 前面的原子至少出现n次，至多出现m次
* | 模式选择，可同时匹配多个pattern，如"python|php"会在"phpudsvpython"中先匹配php
* () 模式单元符，括号中的模式会被当成一个大原子使用！

### 模式修正符

使用方法使re.search(pattern, string, re.I)

* re.I 忽略大小写
* re.M 多行匹配
* re.L 本地化识别
* re.U 根据Unicode字符解析
* re.S 使.包含换行符，即代表所有字符

### 贪婪/懒惰模式

* 贪婪模式，尽可能找符合该pattern最长的字符串，如"p.\*y"匹配"fddsphp345pythony_py"时找到的是"php345pythony_py"
* 懒惰模式，尽可能找符合该pattern最短的字符串，如"p.*?y"匹配"fddspythony_py"时找到的是"php345py"

### 函数

* re.match 从字符串开头比较pattern
* re.match 从字符串任意位置比较pattern
* re.compile+findall 找出所有符合pattern的子字符串
* re.sub(pattern, rep, string, max) 根据正则表达式来实现替换某些字符串的功能

### 例子

"[a-zA-Z]+://\[^\s]*[.com|.cn]" 表示找出结尾是.com或.cn的任意字符串

* [a-zA-Z]表示所有大小写字母
* \+ 表示至少出现过1个字母
* :// 是固定字符串，必须出现
* \[^\s]* 表示出现任意多个 非空白字符
* [.com|.cn] 表示以.com或.cn结尾