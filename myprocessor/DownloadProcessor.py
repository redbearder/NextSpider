# -*- coding: utf-8 -*-

import urllib
import urllib2
import requests
import json
from plugin import qiniuuploader as qn

def DownloadProcessor(download):
    print "downloading with urllib"
    decodejson = json.loads(download)
    urllib.urlretrieve(decodejson['imgurl'], "./download/"+decodejson['imageid']+".jpg")
    qn.qiniuUploader("./download/"+decodejson['imageid']+".jpg", decodejson['imageid']+".jpg")
    pass
