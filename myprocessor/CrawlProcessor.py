# -*- coding: utf-8 -*-
import setting
from lxml import etree
from spiderLib import *

def CrawlProcessor(collectPageUrl, redisclient, mysqlclient = None):
        print 'start to Crawl Page ' + collectPageUrl
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)
            nodes = tree.xpath('//a/@href')
        except Exception, e:
            return
        last = ''
        for each in nodes:
            # if re.match("http://www.gettyimages.cn/\d+", each, re.U):
            if last != each:
                # print each
                last = each
                # print last
                url = 'http://www.gettyimages.cn' + each
                # yield scrapy.Request(url, callback=self.parse_detail)
                while (True):
                    try:
                        if setting.DUPLICATE_SOURCE == 'MYSQL':
                            cursor = mysqlclient.cursor()
                            sql = "insert into " + setting.DUPLICATE_FIELD + "(`" + setting.DUPLICATE_FIELD + "`) values ('" + url + "')"
                            cursor.execute(sql)
                            cursor.close()
                            result = redisclient.lpush(setting.REDIS_COLLECTORQUEUE_1, url)
                        else:
                            saddreturn = redisclient.sadd(setting.DUPLICATE_FIELD, url)
                            if saddreturn == 1:
                                result = redisclient.lpush(setting.REDIS_COLLECTORQUEUE_1, url)

                        print 'Crawl one collector page and success push ' + url
                        # return item
                        break
                    except Exception, e:
                        print e
                        print 'Crawl one collector page and fail push '+url+' and break'
                        break