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
        nodes = tree.xpath('id("wrapper")/div[2]/div[2]/div/ul/li/a/@href')

        for node in nodes:
            if 'www.123rf.com.cn' in node:
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
        except Exception, e:
            print e
            continue

        #get cate page number
        level1catetree = etree.HTML(nodehtml)
        level1catenodes = level1catetree.xpath("id('wrapper')/div[2]/div[3]/div[1]/div/div[2]/div[1]/text()")
        CODEC = 'UTF-8'
        # print pageallnum
        pageallnum = level1catenodes[3].strip()[1:]

        #produce each page url by task url
        #last slash '/' position index
        idx = taskurl[::-1].index('/')
        catekeyword = taskurl[-int(idx):-5]
        current = client.get(setting.REDIS_TASK_CURRENT)
        if current == None:
            current = 1
        if int(current) > int(pageallnum):
            current = 1
            client.set(setting.REDIS_TASK_CURRENT, 1)
        for i in range(int(current), int(pageallnum) + 1):
            if i % setting.REDIS_TASKQUEUE_SAVEFREQUENCY == 0:
                client.set(setting.REDIS_TASK_CURRENT, i)
            ret = 'http://www.123rf.com.cn/search.php?keyword='+catekeyword+'&media_type=0&page='+str(i)
            #ret = cateurl + str(i) + ".html"
            # print ret
            client.lpush(setting.REDIS_CRAWLERQUEUE_1, ret)
            if i == int(pageallnum):
                client.lpop(setting.REDIS_TASKQUEUE)
                client.set(setting.REDIS_TASK_CURRENT, 1)