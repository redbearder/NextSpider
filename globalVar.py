# -*- coding: utf-8 -*-

class GlobalVar:
    proxylist = []
    crawlworkqueue = None
    collectworkqueue = None

def set_proxylist(proxylist):
    GlobalVar.proxylist = proxylist
def get_proxylist():
    return GlobalVar.proxylist
def set_crawlworkqueue(crawlworkqueue):
    GlobalVar.crawlworkqueue = crawlworkqueue
def get_crawlworkqueue():
    return GlobalVar.crawlworkqueue
def set_collectworkqueue(collectworkqueue):
    GlobalVar.collectworkqueue = collectworkqueue
def get_collectworkqueue():
    return GlobalVar.collectworkqueue


