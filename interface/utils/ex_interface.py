#!/usr/bin/env python
#coding:utf-8

import os
from conf_utils import Config
from inter_error import InterErr

class ExInterface(object):
    """调用其他接口的一个工具，可以像使用方法一样使用接口
        所有接口定义在external.ini中
        例如：
        [getUser] #方法名
        protocol = Cgw  ;协议
        interfaceName = opencloud.domain.getDomainList ;接口名
    """
    def __init__(self):
        self.config = Config(name="external")

    def getInterface(self, inf_key):
        """获取对应的接口的协议名和接口名"""

        inf = self.config[inf_key]
        if "protocol" not in inf or "interface" not in inf:
            raise InterErr(InterErr.E_CONFIG_ERR,
                    "protocol or interface does not exist in [%s]" % inf_key)

        return inf

    def getProtocol(self, protocol, interface, data):
        """获取要使用的协议"""
        try:
            str_module = "protocol.%s" % (protocol)
            module = __import__(str_module, fromlist=[""])
            if not hasattr(module, protocol):
                    raise Exception("protocol[%s] is not defined in %.py" % (protocol, protocol))
            return getattr(module, protocol)(data=data, interfaceName=interface)
        except ImportError, e:
            raise Exception("protocol[%s.py] is not exist" % (protocol))
        except Exception, e:
            raise

    def __getattr__(self, inf_key):

        inf = self.getInterface(inf_key)

        def request(req):
            proto = self.getProtocol(inf["protocol"], inf["interface"], req)
            return proto.request(**inf)

        return request

if __name__ == "__main__":
    inf = ExInterface()
    print len(inf.getUser({"offlineStatus":0}))
