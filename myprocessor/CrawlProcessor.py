# -*- coding: utf-8 -*-
import setting
from lxml import etree
from spiderLib import *
import json
import logging

log = logging.getLogger(__name__)

def CrawlProcessor(crawlPageUrl, redisclient, mysqlclient = None):
        log.info('start to Crawl Page ' + crawlPageUrl)
        print 'start to Crawl Page ' + crawlPageUrl
        try:
            url =  'http://www.superimagemarket.com/WebServices/KeyWordsImage.asmx/GetImagesByKeyWords'
            decodejson = json.loads(crawlPageUrl)
            html = posthtml(url,decodejson)
            jsondata = json.loads(html)
        except requests.exceptions.Timeout as e:
            print e
            log.warning(e)
            log.warning('Timeout fail to Crawl one collector page and record '+crawlPageUrl+' and next')
            result=redisclient.lpush(setting.REDIS_COLLECTORQUEUE_1+'_TIMEOUT',crawlPageUrl)
            print 'Timeout fail to Crawl one collector page and record '+crawlPageUrl+' and next'
            raise e
        except Exception, e:
            print e
            log.warning(e)
            raise e
        last = ''
        dictarr = json.loads(jsondata['data'])
        for each in dictarr:
            # if re.match("http://www.gettyimages.cn/\d+", each, re.U):
            if last != each:
                # print each
                last = each
                # print last
                url = 'http://www.superimagemarket.com/ImageDetail.aspx?ImgNum='+each['II_Number']
                # yield scrapy.Request(url, callback=self.parse_detail)
                #need be reconstructed below
                pushCollectorQueue(url, redisclient, mysqlclient,True)
