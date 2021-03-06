# -*- coding: utf-8 -*-

import setting
from web import httpPanel
try:
    import cPickle as pickle
except ImportError:
    import pickle
import redis
import threading
from myprocessor.TaskStarter import TaskStarter
from spider.collector.CollectWorkManager import CollectWorkManager
from spider.crawler.CrawlWorkManager import CrawlWorkManager
from spider.downloader.DownloadWorkManager import DownloadWorkManager
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from datetime import *

if setting.DUPLICATE_SOURCE == 'MYSQL':
    import MySQLdb
    import MySQLdb.cursors

def taskCreator():
    TaskStarter()

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

if __name__ == "__main__":
    loggerName = ''
    BASIC_LOG_PATH = './'
    filename = 'Spider_'+setting.DUPLICATE_FIELD+'.log'
    log = logging.getLogger(loggerName)
    formatter = logging.Formatter('%(asctime)s level-%(levelname)-8s thread-%(thread)-8d %(message)s')
    fileTimeHandler = TimedRotatingFileHandler(BASIC_LOG_PATH + filename, when="midnight", backupCount=30)

    fileTimeHandler.suffix = "%Y%m%d"
    fileTimeHandler.setFormatter(formatter)
    logging.basicConfig(level = logging.WARNING)
    fileTimeHandler.setFormatter(formatter)
    log.addHandler(fileTimeHandler)

    log.info('start Master Spider at '+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    redisproxylist = client.get("PROXYLIST")
    if redisproxylist != None:
        setting.GlobalVar.set_proxylist(redisproxylist)

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

    work_manager = CrawlWorkManager(setting.CRAWLER_NUM)
    collect_work_manager = CollectWorkManager(setting.COLLECTOR_NUM)
    download_work_manager = DownloadWorkManager(setting.DOWNLOADER_NUM)

    taskMgr = TaskWorkManager()

    if setting.WEB_PANEL:
        httpPanel()
