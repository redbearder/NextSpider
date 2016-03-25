# -*- coding: utf-8 -*-
import setting
from lxml import etree
from spiderLib import *

def CrawlProcessor(collectPageUrl, redisclient, mysqlclient = None):
        print 'start to Crawl Page ' + collectPageUrl
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            nodes = tree.xpath("id('search-content')/div/section/section[2]/section[2]/section/article/section/a/@href")
        except requests.exceptions.Timeout as e:
            print e
            result=redisclient.lpush(setting.REDIS_COLLECTORQUEUE_1+'_TIMEOUT',collectPageUrl)
            print 'Timeout fail to Crawl one collector page and record '+collectPageUrl+' and next'
            raise e
        except Exception, e:
            print e
            raise e
        last = ''
        for each in nodes:
            # if re.match("http://www.gettyimages.cn/\d+", each, re.U):
            if last != each:
                # print each
                last = each
                # print last
                url = 'http://www.gettyimages.co.uk'+each
                # yield scrapy.Request(url, callback=self.parse_detail)
                #need be reconstructed below
                pushCollectorQueue(url, redisclient, mysqlclient,True)
