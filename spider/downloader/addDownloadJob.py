# -*- coding: utf-8 -*-
import threading
import setting
from myprocessor import DownloadProcessor
import logging

log = logging.getLogger(__name__)

class addDownloadJob(threading.Thread):
    def __init__(self, work_queue, redisclient):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.redisclient = redisclient
        self.start()

    def addOneMoreJob(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_DOWNLOADQUEUE_1)
            if url != None:
                self.add_job(self.do_job, url)
                break
            else:
                if self.redisclient.exists(setting.REDIS_COLLECTORQUEUE_1) == 1 or self.redisclient.exists(setting.REDIS_DOWNLOADQUEUE_1) == 1 or self.redisclient.exists(setting.REDIS_CRAWLERQUEUE_1) == 1 or self.redisclient.exists(setting.REDIS_TASKQUEUE) == 1:
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
        self.doDownload(args[0])
        self.addOneMoreJob()

    def doDownload(self, download):
        log.info('start to download  ' + download)
        print 'start to download  ' + download
        try:
            #Download Code
            DownloadProcessor.DownloadProcessor(download)
            pass
        except Exception, e:
            print e
            log.warning(e)
            self.redisclient.rpush(setting.REDIS_DOWNLOADQUEUE_1+'_FAIL',download)
            # return

    def run(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_DOWNLOADQUEUE_1)
            if url == None:
                continue
            self.add_job(self.do_job, url)
            break
