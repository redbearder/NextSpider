# -*- coding: utf-8 -*-
import setting
from lxml import etree
from spiderLib import *

def CollectProcessor(collectPageUrl, redisclient, mysqlclient = None):
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            keywordnodes = tree.xpath("id('ulKeylistCN')/ul/dl/dd/span/li/label/text()")

            keywordvar = ''
            for each in keywordnodes:
                keywordvar += each + ','

            #imageid = tree.xpath("id('divPicinfo')/div/table/tbody/tr[6]/td[2]/text()")
            imageid = tree.xpath("id('divPicinfo')/div/table/tr[6]/td[2]/text()")[0].strip()
            imgtitle = tree.xpath("id('divPicinfo')/div/table/tr[1]/td[2]/text()")[0]
            imagetype = tree.xpath("id('divPicinfo')/div/table/tr[8]/td[2]/text()")[0]
            weburl = collectPageUrl
            imgurl = tree.xpath("id('form1')/div[2]/div[3]/div[1]/img/@src")[0]
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
                    print 'Collect one page success push ' + weburl
                    keywordvar = None
                    viewitem = None
                    image_detail = None
                    # return item
                    break
                except Exception, e:
                    print e
                    print 'Collect one page fail push ' + weburl + ' and repeat'
                    continue
        except Exception, e:
                    print e
                    result=redisclient.lpush(setting.REDIS_RESULTQUEUE_1+'_FAIL',collectPageUrl)
                    print 'Collect one page fail push '+collectPageUrl+' and repeat'