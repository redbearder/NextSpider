# -*- coding: utf-8 -*-
import setting
from lxml import etree
import requests
from spiderLib import *

def CollectProcessor(collectPageUrl, redisclient, mysqlclient = None):
        print 'start to Collect Page ' + collectPageUrl
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            keywordnodes1 = tree.xpath("/html/body/div[2]/section/div/div[1]/section[3]/ul/li/a/text()")

            keywordvar = ''
            for each in keywordnodes1:
                keywordvar += each + ','

            #imageid = tree.xpath("id('divPicinfo')/div/table/tbody/tr[6]/td[2]/text()")
            imageid = tree.xpath("/html/body/div[2]/section/div/main/section[2]/dl/dd[3]/text()")[0]
            imgtitle = tree.xpath("/html/body/div[2]/section/div/main/section[2]/div[1]/h1/text()")[0]
            imagetype = tree.xpath("/html/body/div[2]/section/div/main/section[2]/dl/dd[2]/a/text()")[0]
            weburl = collectPageUrl
            imgurl = tree.xpath("/html/body/div[2]/section/div/main/section[1]/div[1]/img/@src")[0]
            keywordvar = keywordvar
            # print keywordvar
            # yield viewitem

            image_detail = {
                'imageid': imageid,
                'imgtitle': imgtitle,
                'imagetype': imagetype,
                'weburl': weburl,
                'imgurl': imgurl,
                'keywordvar': keywordvar,
            }

            while (True):
                try:
                    result = redisclient.lpush(setting.REDIS_RESULTQUEUE_1, image_detail)
                    print 'success to push one page ' + weburl
                    keywordvar = None
                    viewitem = None
                    image_detail = None
                    # return item
                    break
                except Exception, e:
                    print e
                    print 'fail to push one page ' + weburl + ' and repeat'
                    continue
        except requests.exceptions.Timeout as e:
                    print e
                    result=redisclient.lpush(setting.REDIS_RESULTQUEUE_1+'_TIMEOUT',collectPageUrl)
                    print 'Timeout fail to Collect one page and record '+collectPageUrl+' and next'
                    raise e
        except Exception, e:
                    print e
                    result=redisclient.lpush(setting.REDIS_RESULTQUEUE_1+'_FAIL',collectPageUrl)
                    print 'fail to Collect one page and record '+collectPageUrl+' and next'
                    raise e