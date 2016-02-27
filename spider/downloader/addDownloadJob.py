# -*- coding: utf-8 -*-
import threading
import setting
from myprocessor import DownloadProcessor

class addDownloadJob(threading.Thread):
    def __init__(self, work_queue, redisclient):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.redisclient = redisclient
        self.start()

    def addOneMoreJob(self):
        url = self.redisclient.rpop(setting.REDIS_DOWNLOADQUEUE_1)
        if url != None:
            self.add_job(self.do_job, url)

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

    def doDownload(self, downloadUrl):
        print 'start to download  ' + downloadUrl
        try:
            #Download Code
            DownloadProcessor(downloadUrl)
            pass
        except Exception, e:
            return

    def run(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_DOWNLOADQUEUE_1)
            if url == None:
                continue
            self.add_job(self.do_job, url)
            break