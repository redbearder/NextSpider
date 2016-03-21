# -*- coding: utf-8 -*-

import setting
from setting import *
import requests
import random
from urllib2 import URLError, HTTPError
import time

def gethtml(url):
    '''''Fetch the target html'''
    retrytimes=0
    while True:
        proxy = ''
        try:
            headers = setting.REQUEST_HEADER

            if setting.GlobalVar.get_proxylist() == []:
                response = requests.get(url, headers=headers, timeout=setting.REQUEST_TIMEOUT)
            else:
                proxy = random.choice(setting.GlobalVar.get_proxylist())
                proxies = {
                    "http": proxy,
                    "https": proxy,
                }
                response = requests.get(url, headers=headers, timeout=setting.REQUEST_TIMEOUT, proxies=proxies)

            response.encoding = setting.RESPONSE_ENCODING
            # result = response.headers['content-encoding']
            result = response.text

            print "get Page Html successful " + url

            return result
            break
        except requests.exceptions.Timeout as e:
            # Maybe set up for a retry, or continue in a retry loop
            print e
            retrytimes+=1
            if retrytimes > setting.REQUEST_RETRY_TIMES:
                print 'Too Many Retry Times and Give up'
                raise e
                break
            time.sleep(setting.REQUEST_RETRY_INTERVAL)
            continue
        except requests.exceptions.TooManyRedirects as e:
            # Tell the user their URL was bad and try a different one
            print e
            raise e
        except requests.exceptions.RequestException as e:
            #del invalid proxy
            if proxy != '':
                setting.GlobalVar.get_proxylist().remove(proxy)
                client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
                redisproxylist = client.set("PROXYLIST",setting.GlobalVar.get_proxylist())
            print e
            retrytimes+=1
            if retrytimes > setting.REQUEST_RETRY_TIMES:
                print 'Too Many Retry Times and Give up'
                raise e
                break
            time.sleep(setting.REQUEST_RETRY_INTERVAL)
            continue
            # sys.exit(1)
        except URLError, e:
            print e
            raise e
        except Exception, e:
            print e
            raise e