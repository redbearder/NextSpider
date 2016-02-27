# -*- coding: utf-8 -*-
import Queue
import redis
import setting
import DownloadWork
import addDownloadJob

class DownloadWorkManager(object):
    def __init__(self, thread_num=10):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.threads2 = []
        self.redisclient = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW,
                                       db=0)
        self.__init_thread_pool(thread_num)

    """
        初始化线程
    """

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(DownloadWork(self.work_queue))
        # self.threads.append(self.putQueue())
        for i in range(thread_num):
            self.threads2.append(addDownloadJob(self.work_queue, self.redisclient))

    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive(): item.join()