# -*- coding: utf-8 -*-
import threading
import setting
from myprocessor import CollectProcessor

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
        CollectProcessor.CollectProcessor(collectPageUrl, self.redisclient)

    def run(self):
        while True:
            url = self.redisclient.rpop(setting.REDIS_COLLECTORQUEUE_1)
            if url == None:
                continue
            self.add_job(self.do_job, url)
            break