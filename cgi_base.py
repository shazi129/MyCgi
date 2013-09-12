#!/usr/bin/env python
#encoding:utf-8

import traceback
from utils.inter_error import InterErr
from utils.log_utils import Log

class CgiBase(object):
    """cgi框架接口, 适用于的普通cgi和uwsgi"""

    def __init__(self, proto, exception=None):
        self._proto = proto
        self._exception = exception

        self._status = '200 OK'
        self._header = [('Content-Type', 'text/plain')]

    def check_data(self):
        """
        这里放一些数据检查，权限检查神马的
        如果检查不对，请抛出一个异常
        """
        pass

    def do_process(self):
        """
        这里是实际处理的东西
        如果处理不对，请抛出一个异常
        """
        self.gen_json_reply()

    def error(self, e):
        """处理异常，为没错误号的加上错误号"""
        if hasattr(e, "errno") and isinstance(e.errno, int):
            errno = e.errno
        else:
            errno = InterErr.E_INTEFACE_ERR
        self.gen_json_reply(errno, str(e), {})

    def process(self):
        """这才是处理的主方法，也可以改写~~~"""

        #纯粹的错误处理
        if self._exception != None:
           self.error(self._exception)
           return

        try:
            self.check_data()
            self.do_process()
        except Exception, e:
            Log.error(traceback.format_exc())
            self.error(e)

    def reply(self, reply_header):
        reply_header(self._status, self._header)
        try:
            reply_data = self._proto.pack_rsp()
            if isinstance(reply_data, basestring):
                return [reply_data]
            else:
                return reply_data
        except Exception, e:
            Log.error(traceback.format_exc())
            return [str(e)]

    def set_header(self, status, header):
        """根据不同cgi可以有不同的头"""
        self._status = status
        self._header = header

    def gen_json_reply(self, code=0, msg="success", data={}):
        """返回一段json"""
        self._status = '200 OK'
        self._header = [('Content-Type', 'text/plain')]
        self._proto.set_rsp(code=code, msg=msg, data=data)

    def gen_file_reply(self, filename):
        """下载文件的实现"""
        pass
