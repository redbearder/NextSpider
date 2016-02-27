# -*- coding: utf-8 -*-
import setting
from lxml import etree
from spiderLib import *

def CollectProcessor(collectPageUrl, redisclient, mysqlclient = None):
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            nodes = tree.xpath('//div[@class="search"] //ul[@class="clearfix"]')

            keywordvar = ''
            keyword1var = ''
            keyword2var = ''
            keyword3var = ''
            keyword4var = ''
            keyword5var = ''
            i = 1
            # for each in response.doc('div[class="search"] ul[class="clearfix"]').items():
            for each in nodes:
                for each1 in each.xpath('li //label //a/text()'):
                    if i == 1:
                        keyword1var += each1 + ','
                    if i == 2:
                        keyword2var += each1 + ','
                    if i == 3:
                        keyword3var += each1 + ','
                    if i == 4:
                        keyword4var += each1 + ','
                    if i == 5:
                        keyword5var += each1 + ','
                i = i + 1

            keywordvar = keyword1var + keyword2var + keyword3var + keyword4var + keyword5var

            imageid = tree.xpath('//ul[@class="msg"]/li/span/text()')[1]
            imgtitle = tree.xpath('//ul[@class="msg"]/li/span/text()')[0]
            imagetype = tree.xpath('//ul[@class="msg"]/li/span/text()')[2]
            weburl = collectPageUrl
            imgurl = tree.xpath('//div[@class="picmsg"] //p[@class="pic"] //img//@src')[0]
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