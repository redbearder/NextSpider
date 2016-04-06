# -*- coding: utf-8 -*-
import threading
import setting
from myprocessor import CrawlProcessor
import sys

if setting.DUPLICATE_SOURCE == 'MYSQL':
    import MySQLdb
    import MySQLdb.cursors

class addCrawlJob(threading.Thread):
    def __init__(self, work_queue, redisclient):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.redisclient = redisclient
        self.mysqlclient = None
        if setting.DUPLICATE_SOURCE == 'MYSQL':
            self.mysqlclient = MySQLdb.connect(host=setting.MYSQL_SERVER, port=setting.MYSQL_PORT,
                                               user=setting.MYSQL_USER, passwd=setting.MYSQL_PW,
                                               charset=setting.MYSQL_CHARSET, db=setting.MYSQL_DB)
        self.start()

    def addOneMoreJob(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
            if url != None:
                self.add_job(self.do_job, url)
                # print 'addOneMoreJob'
                # print 'add one Crawl job in '+threading.current_thread()
                break
            else:
                if self.redisclient.exists(setting.REDIS_TASKQUEUE) == 1:
                    continue
                else:
                    sys.exit(0)


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
        #print '11111111111111111111111111111111 size is '+str(setting.GlobalVar.get_crawlworkqueue().qsize())

    def getCollectPage(self, crawlPageUrl):
        try:
            CrawlProcessor.CrawlProcessor(crawlPageUrl, self.redisclient, self.mysqlclient)
        except Exception,e:
            print e
            self.redisclient.rpush(setting.REDIS_CRAWLERQUEUE_1+'_FAIL',crawlPageUrl)
            pass

    def run(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_CRAWLERQUEUE_1)
            if url == None:
                continue
            self.add_job(self.do_job, url)
            break