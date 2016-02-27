# -*- coding: utf-8 -*-

import setting
from setting import *
import requests
import random
from urllib2 import URLError, HTTPError

def gethtml(url):
    '''''Fetch the target html'''
    while True:
        proxy = ''
        try:
            headers = setting.REQUEST_HEADER

            if proxylist == []:
                response = requests.get(url, headers=headers)
            else:
                proxy = random.choice(proxylist)
                proxies = {
                    "http": proxy,
                    "https": proxy,
                }
                response = requests.get(url, headers=headers, proxies=proxies)

            response.encoding = setting.RESPONSE_ENCODING
            # result = response.headers['content-encoding']
            result = response.text

            print "get Page Html successful " + url

            return result
            break
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print e
            continue
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print e
            break
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            #del invalid proxy
            proxylist.remove(proxy)
            client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
            redisproxylist = client.set("PROXYLIST",proxylist)
            print e
            continue
            # sys.exit(1)
        except URLError, e:
            print e
            break
        except Exception, e:
            print e
            break