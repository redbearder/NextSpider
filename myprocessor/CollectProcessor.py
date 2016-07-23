# -*- coding: utf-8 -*-
import setting
from lxml import etree
import requests
from spiderLib import *
import json
import urlparse
import logging

log = logging.getLogger(__name__)

# parse html with Dynamic js data
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
'''

def CollectProcessor(collectPageUrl, redisclient, mysqlclient = None):
        log.info('start to Collect Page ' + collectPageUrl)
        print 'start to Collect Page ' + collectPageUrl
        try:
            html = gethtml(collectPageUrl)
            tree = etree.HTML(html)

            #recursion crawl by condition
            #url as recursion condition url
            #pushCollectorQueue(url, redisclient, mysqlclient,True)

            keywordvar = tree.xpath("//meta[@name='Keywords']/@content")[0]

            #imageid = tree.xpath("id('divPicinfo')/div/table/tbody/tr[6]/td[2]/text()")
            query = urlparse.urlparse(collectPageUrl).query
            dictparam = dict([(k,v[0]) for k,v in urlparse.parse_qs(query).items()])
            imageid = dictparam['ImgNum']
            imgtitle = tree.xpath("//meta[@name='Description']/@content")[0]
            imagetype = 'RF'
            weburl = collectPageUrl
            imgurl = tree.xpath("id('wmimg')/@src")[0]
            keywordvar = keywordvar
            # print keywordvar
            # yield viewitem

            image_detail = {}
            image_detail['imageid'] = imageid
            image_detail['imgtitle'] = imgtitle
            image_detail['imagetype'] = imagetype
            image_detail['weburl'] = weburl
            image_detail['imgurl'] = imgurl
            image_detail['keywordvar'] = keywordvar

            jsondata = json.dumps(image_detail)

            while (True):
                try:
                    result = redisclient.lpush(setting.REDIS_RESULTQUEUE_1, jsondata)
                    log.info('success to push one page ' + weburl)
                    print 'success to push one page ' + weburl
                    keywordvar = None
                    viewitem = None
                    image_detail = None
                    # return item
                    if setting.DOWNLOADER_NUM != 0:
                        downloaddata = {}
                        downloaddata['imgurl']=imgurl
                        downloaddata['imageid']=imageid
                        result = redisclient.lpush(setting.REDIS_DOWNLOADQUEUE_1, json.dumps(downloaddata))
                        pass
                    break
                except Exception, e:
                    print e
                    log.warning(e)
                    log.warning('fail to push one page ' + weburl + ' and repeat')
                    print 'fail to push one page ' + weburl + ' and repeat'
                    continue
        except requests.exceptions.Timeout as e:
                    print e
                    log.warning(e)
                    log.warning('Timeout fail to Collect one page and record '+collectPageUrl+' and next')
                    result=redisclient.lpush(setting.REDIS_RESULTQUEUE_1+'_TIMEOUT',collectPageUrl)
                    print 'Timeout fail to Collect one page and record '+collectPageUrl+' and next'
                    raise e
        except Exception, e:
                    print e
                    log.warning(e)
                    log.warning('fail to Collect one page and record '+collectPageUrl+' and next')
                    result=redisclient.lpush(setting.REDIS_RESULTQUEUE_1+'_FAIL',collectPageUrl)
                    print 'fail to Collect one page and record '+collectPageUrl+' and next'
                    raise e