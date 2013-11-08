#!/usr/local/services/python/bin/python
#coding:utf-8

import traceback
import sys
import os
from cgi_frame.cgi_factory import CgiFactory
from cgi_frame.request_field import RequestFieldStorage
from utils.log_utils import Log

def process_header(status, header):
    for item in header:
        sys.stdout.write(": ".join(item))
        sys.stdout.write("\r\n")
    sys.stdout.write("\r\n")
    sys.stdout.flush()

def init_env():
    """设置运行环境"""

    #默认编码
    reload(sys)
    sys.setdefaultencoding('utf8')

    #配置文件
    this_path = os.path.split(os.path.realpath(__file__))[0]
    Log.init(iniPath="%s/config" % this_path)

def application(environ, start_response):

    Log.update_id() #保证每次请求的id都不同

    if "REMOTE_ADDR" in environ:
        Log.info("request from %s" %(str(environ["REMOTE_ADDR"])))

    field = None
    if "wsgi.input" in environ:  #wsgi
        field = RequestFieldStorage(fp=environ['wsgi.input'], environ=environ)
    else:  #普通cgi
        field = RequestFieldStorage(environ=environ)

    try:
        cgi = CgiFactory(field).gen_cgi()
        cgi.process()
        ret = cgi.reply(start_response)
    except Exception, e:
        process_header("200", [('Content-Type', 'text/plain')])
        ret = traceback.format_exc()

    if "REMOTE_ADDR" in environ:
        Log.info("response to %s: %s"  %(str(environ["REMOTE_ADDR"]), str(ret)))
    return ret

if __name__ == "__main__":
    import os
    ret = application(os.environ, process_header)
    for item in ret:
        sys.stdout.write(item)
        sys.stdout.flush()
