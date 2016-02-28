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
        try:
            html = gethtml(setting.start_urls)
        except Exception, e:
            print e
            raise e

        tree = etree.HTML(html)
        nodes = tree.xpath('//a[contains(@href,"/1.html")]/@href')

        for node in nodes:
            if 'www.quanjing.com' in node:
                client.lpush(setting.REDIS_TASKQUEUE, node)

    while True:
        taskurl = client.lpop(setting.REDIS_TASKQUEUE)
        if taskurl == None:
            break
        client.lpush(setting.REDIS_TASKQUEUE, taskurl)

        print 'start to push Crawler Category queue ' + taskurl

        nodehtml = ''
        try:
            nodehtml = gethtml(taskurl)
            level1tree = etree.HTML(nodehtml)
            #level1nodes = level1tree.xpath("id('htmlPageInfoTop')/x:/a[2]/@href")
            level1nodes = level1tree.xpath("id('htmlPageInfoTop')/a[2]/@href")
        except Exception, e:
            print e
            continue

        CODEC = 'UTF-8'
        pageallnum = level1nodes[0][0:-5].split('/')[3]
        # print pageallnum
        idx = taskurl[::-1].index('/')
        cateurl = taskurl[:-int(idx)]
        current = client.get(setting.REDIS_TASK_CURRENT)
        if current == None:
            current = 1
        if int(current) > int(pageallnum):
            current = 1
            client.set(setting.REDIS_TASK_CURRENT, 1)
        for i in range(int(current), int(pageallnum) + 1):
            if i % setting.REDIS_TASKQUEUE_SAVEFREQUENCY == 0:
                client.set(setting.REDIS_TASK_CURRENT, i)

            ret = cateurl + str(i) + ".html"
            # print ret
            client.lpush(setting.REDIS_CRAWLERQUEUE_1, ret)
            if i == int(pageallnum):
                client.lpop(setting.REDIS_TASKQUEUE)
                client.set(setting.REDIS_TASK_CURRENT, 1)