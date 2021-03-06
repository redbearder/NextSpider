# -*- coding: utf-8 -*-

import urllib
import urllib2
import requests
import json
from plugin import qiniuuploader as qn
import logging

log = logging.getLogger(__name__)

def DownloadProcessor(download):
    try:
        decodejson = json.loads(download)
        log.info("downloading with urllib "+decodejson['imageid']+".jpg")
        print "downloading with urllib "+decodejson['imageid']+".jpg"
        urllib.urlretrieve(decodejson['imgurl'], "./download/"+decodejson['imageid']+".jpg")
        qn.qiniuUploader("./download/"+decodejson['imageid']+".jpg", decodejson['imageid']+".jpg")
    except Exception, e:
        print "downloading with urllib "+decodejson['imageid']+".jpg failed"
        log.info("downloading with urllib "+decodejson['imageid']+".jpg failed")
        print e
        raise e
    pass
