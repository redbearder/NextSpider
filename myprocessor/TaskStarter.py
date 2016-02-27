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
    searchurl = 'http://www.gettyimages.cn/showlist.php?searchurl=az04NTgxJm09MSZpdGVtPTYwJng9MCZmPTEmbj0=&beginpage=1&mlt=undefined&ifmemcache=1&datatype=1&total=143739&perpage=60'
    puresearchurl = 'http://www.gettyimages.cn/showlist.php'

    if taskurl == None:
        print setting.start_urls
        # start Redis
        html = gethtml(setting.start_urls)

        tree = etree.HTML(html)
        nodes = tree.xpath('//a[contains(@href,"newsr.php?searchkey=")]/@href')

        for node in nodes:
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
            level1nodes = level1tree.xpath('//div[@id="resultinfo"] //div[@id="totalpage"]/text()')
        except Exception, e:
            continue

        # nodehtml = gethtml(taskurl)
        level1tree = etree.HTML(nodehtml)
        level1nodes = level1tree.xpath('//div[@id="resultinfo"] //div[@id="totalpage"]/text()')

        CODEC = 'UTF-8'
        pageallnum = level1nodes[0].encode(CODEC)
        # print pageallnum
        u = urlparse.urlparse(taskurl)
        q = u.query
        qd = dict(urlparse.parse_qsl(q))
        searchkey = qd['searchkey']
        orasearchurl = 'k=' + searchkey + '&m=1&item=60&x=0&f=1&n='
        searchurlbase64 = base64.b64encode(orasearchurl)

        current = client.get(setting.REDIS_TASK_CURRENT)
        if current == None:
            current = 1
        if int(current) > int(pageallnum):
            current = 1
            client.set(setting.REDIS_TASK_CURRENT, 1)
        for i in range(int(current), int(pageallnum) + 1):
            if i % setting.REDIS_TASKQUEUE_SAVEFREQUENCY == 0:
                client.set(setting.REDIS_TASK_CURRENT, i)
            uu = urlparse.urlparse(searchurl)
            qs = uu.query
            pure_url = searchurl.replace('?' + qs, '')
            qs_dict = dict(urlparse.parse_qsl(qs))
            qs_dict['searchurl'] = searchurlbase64
            qs_dict['beginpage'] = i
            tmp_qs = urllib.unquote(urllib.urlencode(qs_dict))
            ret = puresearchurl + "?" + tmp_qs
            # print ret
            client.lpush(setting.REDIS_CRAWLERQUEUE_1, ret)
            if i == int(pageallnum):
                client.lpop(setting.REDIS_TASKQUEUE)
                client.set(setting.REDIS_TASK_CURRENT, 1)