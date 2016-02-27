# -*- coding: utf-8 -*-

global proxylist
proxylist = []

#web
WEB_PORT = 3333
#REDIS
REDIS_SERVER = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PW=''

#MYSQL
MYSQL_SERVER = "127.0.0.1"
MYSQL_PORT = 3307
MYSQL_USER='root'
MYSQL_PW='root'
MYSQL_CHARSET='utf8'
MYSQL_DB='iso100'

DUPLICATE_SOURCE='MYSQL' #REDIS or MYSQL
DUPLICATE_FIELD='imageurl1'

RESPONSE_ENCODING='gbk'

CRAWLER_NUM=1
COLLECTOR_NUM=3

SLAVE_CRAWLER_NUM=15
SLAVE_COLLECTOR_NUM=40

DOWNLOADER_NUM=30
SLAVE_DOWNLOADER_NUM=30

REDIS_PAGEQUEUE_1='pagequeue1'
REDIS_PAGEQUEUE_2='pagequeue2'

REDIS_TASKQUEUE='REDIS_TASKQUEUE'
REDIS_TASKQUEUE_SAVEFREQUENCY=10
REDIS_TASK_CURRENT='REDIS_TASK_CURRENT'

REDIS_CRAWLERQUEUE_1='REDIS_CRAWLERQUEUE_1'
REDIS_CRAWLERQUEUE_2='REDIS_CRAWLERQUEUE_2'

REDIS_COLLECTORQUEUE_1='REDIS_COLLECTORQUEUE_1'
REDIS_COLLECTORQUEUE_2='REDIS_COLLECTORQUEUE_2'

REDIS_RESULTQUEUE_1='REDIS_RESULTQUEUE_1'
REDIS_RESULTQUEUE_2='REDIS_RESULTQUEUE_2'

REDIS_DOWNLOADQUEUE_1='REDIS_DOWNLOADQUEUE_1'
REDIS_DOWNLOADQUEUE_2='REDIS_DOWNLOADQUEUE_2'

#start_urls=('http://url1','http://url1')
start_urls='http://www.gettyimages.cn/page/icindex.html'

REQUEST_HEADER = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
                "Connection": "keep-alive",
                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
                "Referer": "http://www.gettyimages.cn/newsr.php?searchkey=8227&local=true"
            }


