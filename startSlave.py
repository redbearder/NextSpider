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

class CrawlWorkManager(object):
    def __init__(self, thread_num=10):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.threads2 = []
        self.redisclient = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
        #self.__init_work_queue(work_num)
        #self.init_work_queue()
        self.__init_thread_pool(thread_num)
        #thread.start_new_thread(self.putQueue())


    """
        初始化线程
    """
    def __init_thread_pool(self,thread_num):
        for i in range(thread_num):
           self.threads.append(CrawlWork(self.work_queue))
        #self.threads.append(self.putQueue())
        for i in range(thread_num):
            self.threads2.append(addCrawlJob(self.work_queue,self.redisclient))

    """
        初始化工作队列
    """
    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            print 'queue number'+str(i)
            self.add_job(self.do_job, i)

    def init_work_queue(self):
        for i in range(setting.SLAVE_CRAWLER_NUM):
            print 'queue number'+str(i)
            url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
            self.add_job(self.do_job, url)

    """
        添加一项工作入队
    """
    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))#任务入队，Queue内部实现了同步机制

    def putQueue(self):
        for i in range(setting.SLAVE_CRAWLER_NUM):
            #print 'queue number'+str(i)
            while(True):
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
            if item.isAlive():item.join()


class addCrawlJob(threading.Thread):
    def __init__(self, work_queue, redisclient):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.redisclient = redisclient
        self.start()

    def addOneMoreJob(self):
        url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
        if url != None:
            self.add_job(self.do_job, url)
        #print 'addOneMoreJob'
        #print 'add one Crawl job in '+threading.current_thread()
    """
        添加一项工作入队
    """
    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))#任务入队，Queue内部实现了同步机制

    #具体要做的任务
    def do_job(self,args):
        #time.sleep(0.1)#模拟处理时间
        #print args[0]
        #print 'Crawl one job '+args[0]
        self.getCollectPage(args[0])
        self.addOneMoreJob()

    def getCollectPage(self,collectPageUrl):
        print 'start to Crawl Page '+collectPageUrl
        html = gethtml(collectPageUrl)
        tree = etree.HTML(html)
        nodes = tree.xpath('//a/@href')
        last = ''
        for each in nodes:
                #if re.match("http://www.gettyimages.cn/\d+", each, re.U):
                if last != each:
                    #print each
                    last = each
                    #print last
                    url = 'http://www.gettyimages.cn'+each
                    #yield scrapy.Request(url, callback=self.parse_detail)
                    while(True):
                        try:
                            #self.client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
                            result=self.redisclient.lpush(setting.REDIS_COLLECTORQUEUE_1,url)
                            #print 'Crawl one collector page and success push '+url
                            #return item
                            break
                        except Exception, e:
                            print e
                            #print 'Crawl one collector page and fail push '+url+' and repeat'
                            continue

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
        #死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            do = ''
            args = ''
            try:
                do, args = self.work_queue.get(block=False)#任务异步出队，Queue内部实现了同步机制
                do(args)
                self.work_queue.task_done()#通知系统任务完成
            except Exception, e:
                #print e
                #break
                if do != '' and args != '' :
                    self.work_queue.put((do, list(args)))
                continue

class CollectWorkManager(object):
    def __init__(self, thread_num=10):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.threads2 = []
        self.redisclient = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
        #self.__init_work_queue(work_num)
        #self.init_work_queue()
        self.__init_thread_pool(thread_num)
        #thread.start_new_thread(self.putQueue())


    """
        初始化线程
    """
    def __init_thread_pool(self,thread_num):
        for i in range(thread_num):
           self.threads.append(CollectWork(self.work_queue))
        #self.threads.append(self.putQueue())
        for i in range(thread_num):
            self.threads2.append(addCollectJob(self.work_queue,self.redisclient))

    """
        初始化工作队列
    """
    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            print 'queue number'+str(i)
            self.add_job(self.do_job, i)

    def init_work_queue(self):
        for i in range(setting.SLAVE_CRAWLER_NUM):
            print 'queue number'+str(i)
            url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
            self.add_job(self.do_job, url)

    """
        添加一项工作入队
    """
    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))#任务入队，Queue内部实现了同步机制

    def putQueue(self):
        for i in range(setting.SLAVE_CRAWLER_NUM):
            #print 'queue number'+str(i)
            while(True):
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
            if item.isAlive():item.join()
    #具体要做的任务


class CollectWork(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        #死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            do = ''
            args = ''
            try:
                do, args = self.work_queue.get(block=False)#任务异步出队，Queue内部实现了同步机制
                do(args)
                self.work_queue.task_done()#通知系统任务完成
            except Exception, e:
                #print e
                #break
                if do != '' and args != '' :
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
        #print 'addOneMoreJob'
        #print threading.current_thread()
    """
        添加一项工作入队
    """
    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))#任务入队，Queue内部实现了同步机制

    #具体要做的任务
    def do_job(self,args):
        #time.sleep(0.1)#模拟处理时间
        #print args[0]
        #print 'Collect one page '+args[0]
        self.getResult(args[0])
        self.addOneMoreJob()

    def getResult(self,collectPageUrl):
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            nodes = tree.xpath('//div[@class="search"] //ul[@class="clearfix"]')
            keywordvar = ''
            keyword1var = ''
            keyword2var = ''
            keyword3var = ''
            keyword4var = ''
            keyword5var = ''
            i=1
            #for each in response.doc('div[class="search"] ul[class="clearfix"]').items():
            for each in nodes:
                for each1 in each.xpath('li //label //a/text()'):
                    if i == 1:
                        keyword1var += each1+','
                    if i == 2:
                        keyword2var += each1+','
                    if i == 3:
                        keyword3var += each1+','
                    if i == 4:
                        keyword4var += each1+','
                    if i == 5:
                        keyword5var += each1+','
                i = i + 1

            keywordvar = keyword1var+keyword2var+keyword3var+keyword4var+keyword5var

            imageid = tree.xpath('//ul[@class="msg"]/li/span/text()')[1]
            imgtitle = tree.xpath('//ul[@class="msg"]/li/span/text()')[0]
            imagetype = tree.xpath('//ul[@class="msg"]/li/span/text()')[2]
            weburl = collectPageUrl
            imgurl = tree.xpath('//div[@class="picmsg"] //p[@class="pic"] //img//@src')[0]
            keywordvar = keywordvar
            #print keywordvar
            #yield viewitem
            '''
            image_detail = {
                    'imageid':imageid,
                    'imgtitle':imgtitle,
                    'imagetype':imagetype,
                    'weburl':weburl,
                    'imgurl':imgurl,
                    'keywordvar':keywordvar,
                }
            '''
            image_detail = {
                    'imageid':imageid
                }
            while(True):
                try:
                    #self.client = redis.Redis(host=self.REDIS_SERVER, port=self.REDIS_PORT, password=self.REDIS_PW, db=0)
                    result=self.redisclient.lpush(setting.REDIS_RESULTQUEUE_1,image_detail)
                    print 'Collect one page success push '+weburl
                    keywordvar=None
                    viewitem=None
                    image_detail=None
                    #return item
                    break
                except Exception, e:
                    print e
                    print 'Collect one page fail push '+weburl+' and repeat'
                    continue
        except Exception, e:
                    print e
                    result=self.redisclient.lpush(setting.REDIS_RESULTQUEUE_1+'_FAIL',collectPageUrl)
                    print 'Collect one page fail push '+collectPageUrl+' and repeat'



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
               "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
               "Referer": "http://www.gettyimages.cn/newsr.php?searchkey=8227&local=true"
            }
            response = requests.get(url,headers=headers)
            response.encoding='gbk'
            #result = response.headers['content-encoding']
            result = response.text
            # insert into the html_cache.db
            #curs.execute("insert into htmls values(?,?,?);", (url,serialize(result),len(result)))
            #conn.commit()

            print "get Page Html successful " + url

            return  result
            break
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print e
            continue
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print e
            continue
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print e
            continue
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
            continue

def pushTaskQueue(taskobject, taskurl):
    print 'pushCrawlerQueue'

def pushCrawlerQueue(url):
    print 'pushCrawlerQueue'

def pushCollectorQueue(url):
    print 'pushCollectorQueue'

if __name__=="__main__":
    work_manager =  CrawlWorkManager(setting.SLAVE_CRAWLER_NUM)#或者work_manager =  WorkManager(10000, 20)
    collect_work_manager =  CollectWorkManager(setting.SLAVE_COLLECTOR_NUM)#或者work_manager =  WorkManager(10000, 20)
    #work_manager.wait_allcomplete()
    #work_manager.init_work_queue()
