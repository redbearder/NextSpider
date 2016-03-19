# -*- coding: utf-8 -*-
import setting
import redis
from setting import *
from flask import Flask, request, abort, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', crawl_work_queue_size=setting.GlobalVar.get_crawlworkqueue().qsize(), collect_work_queue_size=setting.GlobalVar.get_collectworkqueue().qsize())


@app.route('/proxy')
def proxy():
    return render_template('proxy.html', proxylist=setting.GlobalVar.get_proxylist(),num=len(setting.GlobalVar.get_proxylist()))


@app.route('/addproxy/<proxyprotocol>/<proxyip>/<proxyport>')
def proxy1(proxyprotocol, proxyip, proxyport):
    oneproxy = proxyprotocol + '://' + proxyip + ':' + proxyport
    setting.GlobalVar.get_proxylist().append(oneproxy)
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    redisproxylist = client.set("PROXYLIST",setting.GlobalVar.get_proxylist())
    return render_template('proxy.html', proxylist=setting.GlobalVar.get_proxylist(),num=len(setting.GlobalVar.get_proxylist()))

@app.route('/delproxy/<proxyid>')
def proxy2(proxyid):
    try:
        del setting.GlobalVar.get_proxylist()[int(proxyid)]
    except Exception, e:
        pass
    client = redis.Redis(host=setting.REDIS_SERVER, port=setting.REDIS_PORT, password=setting.REDIS_PW, db=0)
    redisproxylist = client.set("PROXYLIST",setting.GlobalVar.get_proxylist())
    return render_template('proxy.html', proxylist=setting.GlobalVar.get_proxylist(),num=len(setting.GlobalVar.get_proxylist()))


def httpPanel():
    import gevent
    from gevent.pywsgi import WSGIServer
    from jinja2 import FileSystemLoader
    import os, sys

    # root_path = os.path.dirname()

    root_path = sys.path[0]
    app.jinja_loader = FileSystemLoader(os.path.join(root_path, 'web/templates'))
    app.static_folder = os.path.join(root_path, 'web/static')

    app.debug = True
    http_server = WSGIServer(("0.0.0.0", WEB_PORT), app, log=None, handler_class=None)
    try:
        http_server.serve_forever()
        # pass
    except KeyboardInterrupt:
        pass