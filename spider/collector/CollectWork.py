# -*- coding: utf-8 -*-
import threading

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