# -*- coding: utf-8 -*-
__author__ = 'Administrator'

import requests
import setting
import urllib2
import urlparse
import base64
import urllib
from urllib2 import URLError, HTTPError

try:
    import cPickle as pickle
except ImportError:
    import pickle
from lxml import etree
from spider.collector import *
from spider.crawler import *
import redis
import Queue
import threading
import time
import thread
import random
import socket
import SocketServer

if setting.DUPLICATE_SOURCE == 'MYSQL':
    import MySQLdb
    import MySQLdb.cursors

# from gevent import monkey
# monkey.patch_all()

from flask import Flask, request, abort, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/proxy')
def proxy():
    '''
    result = ''
    for p in proxylist:
        result = result + str(p) + '\n'
    '''
    return render_template('proxy.html', proxylist=proxylist,num=len(proxylist))
    # return result


@app.route('/addproxy/<proxyprotocol>/<proxyip>/<proxyport>')
def proxy1(proxyprotocol, proxyip, proxyport):
    oneproxy = proxyprotocol + '://' + proxyip + ':' + proxyport
    proxylist.append(oneproxy)
    # proxylisttmp = list(set(proxylist))
    # proxylist = proxylisttmp
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    redisproxylist = client.set("PROXYLIST",proxylist)
    return render_template('proxy.html', proxylist=proxylist,num=len(proxylist))
    # return result

@app.route('/delproxy/<proxyid>')
def proxy2(proxyid):
    try:
        del proxylist[int(proxyid)]
    except Exception, e:
        pass
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    redisproxylist = client.set("PROXYLIST",proxylist)
    return render_template('proxy.html', proxylist=proxylist,num=len(proxylist))


'''
@app.route('/wssh/<hostname>/<username>')
def connect(hostname, username):
    app.logger.debug('{remote} -> {username}@{hostname}: {command}'.format(
            remote=request.remote_addr,
            username=username,
            hostname=hostname,
            command=request.args['run'] if 'run' in request.args else
                '[interactive shell]'
        ))
'''


def httpPanel():
    from gevent.pywsgi import WSGIServer
    from jinja2 import FileSystemLoader
    import os, sys

    # root_path = os.path.dirname()

    root_path = sys.path[0]
    app.jinja_loader = FileSystemLoader(os.path.join(root_path, 'templates'))
    app.static_folder = os.path.join(root_path, 'static')

    app.debug = True
    '''
    http_server = WSGIServer(('0.0.0.0', 3333), app,
        log=None,
        handler_class=WebSocketHandler)
    '''
    http_server = WSGIServer(("0.0.0.0", 3333), app, log=None, handler_class=None)
    try:
        '''
        server_thread = threading.Thread(target=http_server.serve_forever())
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)
        '''
        http_server.serve_forever()
        # pass
    except KeyboardInterrupt:
        pass

def taskCreator():
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    taskurl = client.lpop(setting.REDIS_TASKQUEUE)
    searchurl = 'http://www.gettyimages.cn/showlist.php?searchurl=az04NTgxJm09MSZpdGVtPTYwJng9MCZmPTEmbj0=&beginpage=1&mlt=undefined&ifmemcache=1&datatype=1&total=143739&perpage=60'
    puresearchurl = 'http://www.gettyimages.cn/showlist.php'

    if taskurl == None:
        print setting.start_urls
        # start Redis
        html = gethtml(setting.start_urls)

        tree = etree.HTML(html)
        nodes = tree.xpath('//a[contains(@href,"newsr.php?searchkey=")]/@href')

        for node in nodes:
            client.lpush(setting.REDIS_TASKQUEUE, node)

    while True:
        taskurl = client.lpop(setting.REDIS_TASKQUEUE)
        if taskurl == None:
            break
        client.lpush(setting.REDIS_TASKQUEUE, taskurl)

        print 'start to push Crawler Category queue ' + taskurl

        nodehtml = ''
        try:
            nodehtml = gethtml(taskurl)
            level1tree = etree.HTML(nodehtml)
            level1nodes = level1tree.xpath('//div[@id="resultinfo"] //div[@id="totalpage"]/text()')
        except Exception, e:
            continue

        # nodehtml = gethtml(taskurl)
        level1tree = etree.HTML(nodehtml)
        level1nodes = level1tree.xpath('//div[@id="resultinfo"] //div[@id="totalpage"]/text()')

        CODEC = 'UTF-8'
        pageallnum = level1nodes[0].encode(CODEC)
        # print pageallnum
        u = urlparse.urlparse(taskurl)
        q = u.query
        qd = dict(urlparse.parse_qsl(q))
        searchkey = qd['searchkey']
        orasearchurl = 'k=' + searchkey + '&m=1&item=60&x=0&f=1&n='
        searchurlbase64 = base64.b64encode(orasearchurl)

        current = client.get(setting.REDIS_TASK_CURRENT)
        if current == None:
            current = 1
        if int(current) > int(pageallnum):
            current = 1
            client.set(setting.REDIS_TASK_CURRENT, 1)
        for i in range(int(current), int(pageallnum) + 1):
            if i % setting.REDIS_TASKQUEUE_SAVEFREQUENCY == 0:
                client.set(setting.REDIS_TASK_CURRENT, i)
            uu = urlparse.urlparse(searchurl)
            qs = uu.query
            pure_url = searchurl.replace('?' + qs, '')
            qs_dict = dict(urlparse.parse_qsl(qs))
            qs_dict['searchurl'] = searchurlbase64
            qs_dict['beginpage'] = i
            tmp_qs = urllib.unquote(urllib.urlencode(qs_dict))
            ret = puresearchurl + "?" + tmp_qs
            # print ret
            client.lpush(setting.REDIS_CRAWLERQUEUE_1, ret)
            if i == int(pageallnum):
                client.lpop(setting.REDIS_TASKQUEUE)
                client.set(setting.REDIS_TASK_CURRENT, 1)

class TaskWorkManager(object):
    def __init__(self, thread_num=1):
        self.threads = []
        self.__init_thread_pool(thread_num)

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(TaskWork())

class TaskWork(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        taskCreator()

def taskMain():
    server_thread = threading.Thread(target=taskCreator())
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("taskCreator loop running in thread:", server_thread.name)

class CrawlWorkManager(object):
    def __init__(self, thread_num=10):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.threads2 = []
        self.redisclient = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW,
                                       db=0)
        # self.__init_work_queue(work_num)
        # self.init_work_queue()
        self.__init_thread_pool(thread_num)
        # thread.start_new_thread(self.putQueue())

    """
        初始化线程
    """

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(CrawlWork(self.work_queue))
        # self.threads.append(self.putQueue())
        for i in range(thread_num):
            self.threads2.append(addCrawlJob(self.work_queue, self.redisclient))

    """
        初始化工作队列
    """

    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            print 'queue number' + str(i)
            self.add_job(self.do_job, i)

    def init_work_queue(self):
        for i in range(setting.CRAWLER_NUM):
            print 'queue number' + str(i)
            url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
            self.add_job(self.do_job, url)

    """
        添加一项工作入队
    """

    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))  # 任务入队，Queue内部实现了同步机制

    def putQueue(self):
        for i in range(setting.CRAWLER_NUM):
            # print 'queue number'+str(i)
            while (True):
                url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
                if url == None:
                    continue
                self.add_job(self.do_job, url)
                break

    """
        等待所有线程运行完毕
    """

    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive(): item.join()


class addCrawlJob(threading.Thread):
    def __init__(self, work_queue, redisclient):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.redisclient = redisclient
        if setting.DUPLICATE_SOURCE == 'MYSQL':
            self.mysqlclient = MySQLdb.connect(host=setting.MYSQL_SERVER, port=setting.MYSQL_PORT,
                                               user=setting.MYSQL_USER, passwd=setting.MYSQL_PW,
                                               charset=setting.MYSQL_CHARSET, db=setting.MYSQL_DB)
        self.start()

    def addOneMoreJob(self):
        url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
        if url != None:
            self.add_job(self.do_job, url)
            # print 'addOneMoreJob'
            # print 'add one Crawl job in '+threading.current_thread()

    """
        添加一项工作入队
    """

    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))  # 任务入队，Queue内部实现了同步机制

    # 具体要做的任务
    def do_job(self, args):
        # time.sleep(0.1)#模拟处理时间
        # print args[0]
        # print 'Crawl one job '+args[0]
        self.getCollectPage(args[0])
        self.addOneMoreJob()

    def getCollectPage(self, collectPageUrl):
        print 'start to Crawl Page ' + collectPageUrl
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            nodes = tree.xpath('//a/@href')
        except Exception, e:
            return
        last = ''
        for each in nodes:
            # if re.match("http://www.gettyimages.cn/\d+", each, re.U):
            if last != each:
                # print each
                last = each
                # print last
                url = 'http://www.gettyimages.cn' + each
                # yield scrapy.Request(url, callback=self.parse_detail)
                while (True):
                    try:
                        if setting.DUPLICATE_SOURCE == 'MYSQL':
                            cursor = self.mysqlclient.cursor()
                            sql = "insert into " + setting.DUPLICATE_FIELD + "(`" + setting.DUPLICATE_FIELD + "`) values ('" + url + "')"
                            cursor.execute(sql)
                            cursor.close()
                            result = self.redisclient.lpush(setting.REDIS_COLLECTORQUEUE_1, url)
                        else:
                            saddreturn = self.redisclient.sadd(setting.DUPLICATE_FIELD, url)
                            if saddreturn == 1:
                                result = self.redisclient.lpush(setting.REDIS_COLLECTORQUEUE_1, url)

                        print 'Crawl one collector page and success push ' + url
                        # return item
                        break
                    except Exception, e:
                        print e
                        # print 'Crawl one collector page and fail push '+url+' and repeat'
                        break

    def run(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
            if url == None:
                continue
            self.add_job(self.do_job, url)
            break


class CrawlWork(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        # 死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            do = ''
            args = ''
            try:
                do, args = self.work_queue.get(block=False)  # 任务异步出队，Queue内部实现了同步机制
                do(args)
                self.work_queue.task_done()  # 通知系统任务完成
            except Exception, e:
                # print e
                # break
                if do != '' and args != '':
                    self.work_queue.put((do, list(args)))
                continue


class CollectWorkManager(object):
    def __init__(self, thread_num=10):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.threads2 = []
        self.redisclient = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW,
                                       db=0)
        # self.__init_work_queue(work_num)
        # self.init_work_queue()
        self.__init_thread_pool(thread_num)
        # thread.start_new_thread(self.putQueue())

    """
        初始化线程
    """

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(CollectWork(self.work_queue))
        # self.threads.append(self.putQueue())
        for i in range(thread_num):
            self.threads2.append(addCollectJob(self.work_queue, self.redisclient))

    """
        初始化工作队列
    """

    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            print 'queue number' + str(i)
            self.add_job(self.do_job, i)

    def init_work_queue(self):
        for i in range(setting.CRAWLER_NUM):
            print 'queue number' + str(i)
            url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
            self.add_job(self.do_job, url)

    """
        添加一项工作入队
    """

    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))  # 任务入队，Queue内部实现了同步机制

    def putQueue(self):
        for i in range(setting.CRAWLER_NUM):
            # print 'queue number'+str(i)
            while (True):
                url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
                if url == None:
                    continue
                self.add_job(self.do_job, url)
                break

    """
        等待所有线程运行完毕
    """

    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive(): item.join()
            # 具体要做的任务


class CollectWork(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        # 死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            do = ''
            args = ''
            try:
                do, args = self.work_queue.get(block=False)  # 任务异步出队，Queue内部实现了同步机制
                do(args)
                self.work_queue.task_done()  # 通知系统任务完成
            except Exception, e:
                # print e
                # break
                if do != '' and args != '':
                    self.work_queue.put((do, list(args)))
                continue


class addCollectJob(threading.Thread):
    def __init__(self, work_queue, redisclient):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.redisclient = redisclient
        self.start()

    def addOneMoreJob(self):
        url = self.redisclient.rpop(setting.REDIS_COLLECTORQUEUE_1)
        if url != None:
            self.add_job(self.do_job, url)
            # print 'addOneMoreJob'
            # print threading.current_thread()

    """
        添加一项工作入队
    """

    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))  # 任务入队，Queue内部实现了同步机制

    # 具体要做的任务
    def do_job(self, args):
        # time.sleep(0.1)#模拟处理时间
        # print args[0]
        # print 'Collect one page '+args[0]
        self.getResult(args[0])
        self.addOneMoreJob()

    def getResult(self, collectPageUrl):
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            nodes = tree.xpath('//div[@class="search"] //ul[@class="clearfix"]')
        except Exception, e:
            return

        keywordvar = ''
        keyword1var = ''
        keyword2var = ''
        keyword3var = ''
        keyword4var = ''
        keyword5var = ''
        i = 1
        # for each in response.doc('div[class="search"] ul[class="clearfix"]').items():
        for each in nodes:
            for each1 in each.xpath('li //label //a/text()'):
                if i == 1:
                    keyword1var += each1 + ','
                if i == 2:
                    keyword2var += each1 + ','
                if i == 3:
                    keyword3var += each1 + ','
                if i == 4:
                    keyword4var += each1 + ','
                if i == 5:
                    keyword5var += each1 + ','
            i = i + 1

        keywordvar = keyword1var + keyword2var + keyword3var + keyword4var + keyword5var

        imageid = tree.xpath('//ul[@class="msg"]/li/span/text()')[1]
        imgtitle = tree.xpath('//ul[@class="msg"]/li/span/text()')[0]
        imagetype = tree.xpath('//ul[@class="msg"]/li/span/text()')[2]
        weburl = collectPageUrl
        imgurl = tree.xpath('//div[@class="picmsg"] //p[@class="pic"] //img//@src')[0]
        keywordvar = keywordvar
        # print keywordvar
        # yield viewitem

        image_detail = {
            'imageid': imageid,
            'imgtitle': imgtitle,
            'imagetype': imagetype,
            'weburl': weburl,
            'imgurl': imgurl,
            'keywordvar': keywordvar,
        }

        while (True):
            try:
                # self.client = redis.Redis(host=self.REDIS_SERVER, port=self.REDIS_PORT, password=self.REDIS_PW, db=0)
                result = self.redisclient.lpush(setting.REDIS_RESULTQUEUE_1, image_detail)
                print 'Collect one page success push ' + weburl
                keywordvar = None
                viewitem = None
                image_detail = None
                # return item
                break
            except Exception, e:
                print e
                print 'Collect one page fail push ' + weburl + ' and repeat'
                continue

    def run(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_COLLECTORQUEUE_1)
            if url == None:
                continue
            self.add_job(self.do_job, url)
            break


def gethtml(url):
    '''''Fetch the target html'''
    while True:
        proxy = ''
        try:
            # look up the html_cache.db first
            '''
            curs.execute("select * from htmls where url=?;" ,(url,))
            row = curs.fetchone()
            if row:
                # find the target
                #print deserialize(str(row[1]))
                return deserialize(str(row[1]))
            '''
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
                "Connection": "keep-alive",
                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
                "Referer": "http://www.gettyimages.cn/newsr.php?searchkey=8227&local=true"
            }

            if proxylist == []:
                response = requests.get(url, headers=headers)
            else:
                proxy = random.choice(proxylist)
                proxies = {
                    "http": proxy,
                    "https": proxy,
                }
                response = requests.get(url, headers=headers, proxies=proxies)
            # response = requests.get(url,headers=headers)
            response.encoding = setting.RESPONSE_ENCODING
            # result = response.headers['content-encoding']
            result = response.text
            # insert into the html_cache.db
            # curs.execute("insert into htmls values(?,?,?);", (url,serialize(result),len(result)))
            # conn.commit()

            print "get Page Html successful " + url

            return result
            break
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print e
            continue
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print e
            break
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            #del invalid proxy
            proxylist.remove(proxy)
            client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
            redisproxylist = client.set("PROXYLIST",proxylist)
            print e
            continue
            # sys.exit(1)
        except URLError, e:
            '''
            if hasattr(e, 'reason'):
                print 'Failed to reach a server.'
                print 'Reason: ', e.reason
                #return 'None'
            elif hasattr(e, 'code'):
                print 'The server couldn not fulfill the request'
                print 'Reason: ', e.reason
            '''
            print e
            break
        except Exception, e:
            print e
            break




def pushTaskQueue(taskobject, taskurl):
    print 'pushCrawlerQueue'


def pushCrawlerQueue(url):
    print 'pushCrawlerQueue'


def pushCollectorQueue(url):
    print 'pushCollectorQueue'


if __name__ == "__main__":
    global proxylist
    proxylist = []
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    redisproxylist = client.get("PROXYLIST")
    if redisproxylist != None:
        proxylist = redisproxylist

    if setting.DUPLICATE_SOURCE == 'MYSQL':
        mysqlclient = MySQLdb.connect(host=setting.MYSQL_SERVER, port=setting.MYSQL_PORT, user=setting.MYSQL_USER,
                                      passwd=setting.MYSQL_PW, charset=setting.MYSQL_CHARSET, db=setting.MYSQL_DB)
        cursor = mysqlclient.cursor()
        sql = "CREATE TABLE IF NOT EXISTS `" + setting.DUPLICATE_FIELD + "` (\
              `id` int(11) NOT NULL AUTO_INCREMENT,\
              `" + setting.DUPLICATE_FIELD + "` varchar(100) COLLATE utf8_unicode_ci NOT NULL,\
              `createdtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,\
              PRIMARY KEY (`id`),\
              UNIQUE KEY `" + setting.DUPLICATE_FIELD + "` (`" + setting.DUPLICATE_FIELD + "`)\
            ) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;"
        cursor.execute(sql)
        cursor.close()

    work_manager = CrawlWorkManager(setting.CRAWLER_NUM)  # 或者work_manager =  WorkManager(10000, 20)
    collect_work_manager = CollectWorkManager(setting.COLLECTOR_NUM)  # 或者work_manager =  WorkManager(10000, 20)

    taskMgr = TaskWorkManager()
    #thread.start_new_thread(taskCreator(), ())
    httpPanel()
