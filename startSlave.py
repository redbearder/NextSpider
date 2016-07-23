# -*- coding: utf-8 -*-

import setting
from spider.collector.CollectWorkManager import CollectWorkManager
from spider.crawler.CrawlWorkManager import CrawlWorkManager
from spider.downloader.DownloadWorkManager import DownloadWorkManager
try:
    import cPickle as pickle
except ImportError:
    import pickle
import redis
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from datetime import *

if __name__=="__main__":
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

    log.info('start Slave Spider at '+datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    redisproxylist = client.get("PROXYLIST")
    if redisproxylist != None:
        setting.GlobalVar.set_proxylist(redisproxylist)
    work_manager =  CrawlWorkManager(setting.SLAVE_CRAWLER_NUM)
    collect_work_manager =  CollectWorkManager(setting.SLAVE_COLLECTOR_NUM)
    download_work_manager = DownloadWorkManager(setting.SLAVE_DOWNLOADER_NUM)

    while True:
        time.sleep(10)
        redisproxylist = client.get("PROXYLIST")
        if redisproxylist != None:
            setting.GlobalVar.set_proxylist(redisproxylist)
        else:
            proxylist = []
            setting.GlobalVar.set_proxylist(proxylist)

