# -*- coding: utf-8 -*-

import redis
import setting
from lxml import etree
from spiderLib import gethtml
from spiderLib import posthtml
import urlparse
import base64
import urllib
import json

def TaskStarter():
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    taskurl = client.lpop(setting.REDIS_TASKQUEUE)

    if taskurl == None:
        print setting.start_urls
        # start Redis
        try:
            html = posthtml(setting.start_urls,{"top":30})
        except Exception, e:
            print e
            raise e

        jsondata = json.loads(html)
        for node in jsondata:
            client.lpush(setting.REDIS_TASKQUEUE, node['CM_Keywords'])

    while True:
        taskurl = client.lpop(setting.REDIS_TASKQUEUE)
        if taskurl == None:
            break
        client.lpush(setting.REDIS_TASKQUEUE, taskurl)

        print 'start to push Crawler Category queue ' + taskurl

        nodehtml = ''
        try:
            url =  'http://www.superimagemarket.com/WebServices/KeyWordsImage.asmx/GetImagesByKeyWords'
            data = {}
            data['pageSize']=99
            data['pageIndex']=1
            data['KeyWords']=taskurl
            data['People']=0
            data['Color']=0
            data['Formats']=0
            data['MediaType']=0
            data['Price']=0
            data['Rating']=0
            data['Licence']=0
            data['fldSort']='Best Match'
            data['Order']=1
            #print data
            jsondata = posthtml(url,data)
        except Exception, e:
            print e
            continue
        #get cate page number

        CODEC = 'UTF-8'
        # print pageallnum
        decodedata = json.loads(jsondata)
        pageallnum = int(int(decodedata['count'])/99)+1

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
            ret = 'http://www.superimagemarket.com/WebServices/KeyWordsImage.asmx/GetImagesByKeyWords'
            #ret = cateurl + str(i) + ".html"
            #query = urlparse.urlparse(taskurl).query
            #qsdict =  dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])
            data = {}
            data['pageSize']=99
            data['pageIndex']=i
            data['KeyWords']=taskurl.lower()
            data['People']=0
            data['Color']=0
            data['Formats']=0
            data['MediaType']=0
            data['Price']=0
            data['Rating']=0
            data['Licence']=0
            data['fldSort']='Best Match'
            data['Order']=1
            # print ret
            client.lpush(setting.REDIS_CRAWLERQUEUE_1, json.dumps(data))
            if i == int(pageallnum):
                client.lpop(setting.REDIS_TASKQUEUE)
                client.set(setting.REDIS_TASK_CURRENT, 1)