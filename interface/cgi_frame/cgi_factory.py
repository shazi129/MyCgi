#!/usr/bin/env python
#coding: utf-8

import traceback

from utils.log_utils import Log
from cgi_base import CgiBase
from protocol import Protocol
from utils.inter_error import InterErr

class CgiFactory(object):
    """cgi 工厂，用于生成各种cgi"""

    def __init__(self, field):
        self._field = field
        self._proto = Protocol()

    def gen_error_cgi(self, errno, errmsg):
        """产生一个错误处理的cgi"""
        cgi = CgiBase(self._proto)
        cgi.gen_json_reply(errno, errmsg)
        return cgi

    def gen_cgi(self):
        try:
            self._proto.unpackReq(self._field)
            interfaceName = self._proto.req["interfaceName"]

            intent = interfaceName.split(".");
            if len(intent) != 2:
                raise InterErr(InterErr.E_INVALID_PARA,
                        "interfaceName[%s] is invalid" % interfaceName)

            intent[0] = intent[0].strip()
            intent[1] = intent[1].strip()
            str_module = "worker.%s.%s" % (intent[0], intent[1])

            module = __import__(str_module, fromlist=[""])

            if not hasattr(module, intent[1]):
                raise InterErr(InterErr.E_NO_INTERFACE,
                        "no that interfaceName[%s]" % intent[1])

            inter_obj = getattr(module, intent[1])(self._proto)
            return inter_obj

        except ImportError, e:
            Log.error(traceback.format_exc())
            e = InterErr(InterErr.E_INVALID_PARA, "invalid interfaceName")
            return CgiBase(self._proto, exception=e)
        except Exception, e:
            Log.error(traceback.format_exc())
            return CgiBase(self._proto, exception=e)
