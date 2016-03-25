# -*- coding: utf-8 -*-

import redis
import setting
from lxml import etree
from spiderLib import gethtml
import urlparse
import base64
import urllib

def TaskStarter():
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    taskurl = client.lpop(setting.REDIS_TASKQUEUE)

    if taskurl == None:
        print setting.start_urls
        # start Redis
        node = 'http://www.gettyimages.co.uk/search/2/image?excludenudity=true&family=creative&license=rf&page=1&sort=best'
        client.lpush(setting.REDIS_TASKQUEUE, node)

    while True:
        taskurl = client.lpop(setting.REDIS_TASKQUEUE)
        if taskurl == None:
            break
        client.lpush(setting.REDIS_TASKQUEUE, taskurl)

        print 'start to push Crawler Category queue ' + taskurl


        pageallnum = 151582

        #produce each page url by task url
        current = client.get(setting.REDIS_TASK_CURRENT)
        if current == None:
            current = 1
        if int(current) > int(pageallnum):
            current = 1
            client.set(setting.REDIS_TASK_CURRENT, 1)
        for i in range(int(current), int(pageallnum) + 1):
            if i % setting.REDIS_TASKQUEUE_SAVEFREQUENCY == 0:
                client.set(setting.REDIS_TASK_CURRENT, i)
            ret = 'http://www.gettyimages.co.uk/search/2/image?excludenudity=true&family=creative&license=rf&page='+str(i)+'&sort=best'
            #ret = cateurl + str(i) + ".html"
            # print ret
            client.lpush(setting.REDIS_CRAWLERQUEUE_1, ret)
            if i == int(pageallnum):
                client.lpop(setting.REDIS_TASKQUEUE)
                client.set(setting.REDIS_TASK_CURRENT, 1)