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


if __name__=="__main__":
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

