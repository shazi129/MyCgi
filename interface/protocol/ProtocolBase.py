#coding:utf-8

import time
import os
import ConfigParser
from utils.inter_error import InterErr
from utils.log_utils import Log

class ProtocolBase(object):

    def __init__(self, **kargs):
        self.req = kargs
        self.rsp = {}
        self.path = os.path.split(os.path.realpath(__file__))[0]
        self.config = {}
        self.getConfig("global")

    def getConfig(self, name):
        """获取协议相关配置, name为配置中的协议名"""

        confile = "%s/../config/protocol.ini" % self.path
        confParser = ConfigParser.SafeConfigParser()
        inis = confParser.read(confile)

        if len(inis) == 0:
            raise Exception("cannot find config file[%s]" % confile)
        if name not in confParser.sections():
            return

        for item in confParser.options(name):
            self.config[item] = confParser.get(name, item)

    def setRsp(self, **kwargs):
        self.rsp = kwargs

    def unpackReq(self, field):
        """将符合本协议的http请求解包, req"""
        pass

    def packRsp(self, **kargs):
        """打包成符合本协议的返回包"""
        pass

    def unpackRsp(self, rsp):
        """将符合本协议的返回包解包，返回数据字段"""
        pass

    def packReq(self):
        """打包成符合本协议的请求包"""
        pass

    def do_request(self, req):
        """实际的请求"""
        pass

    def request(self, **kwargs):
        """对请求的封装，包括重试等"""

        #从参数中读取url
        if "url" in kwargs and kwargs["url"]:
            self.config["url"] = kwargs["url"]
        if "url" not in self.config:
            raise InterErr(InterErr.E_CONFIG_ERR, "no url config")

        #从参数中读取timeout
        if "timeout" in kwargs and kwargs["timeout"]:
            self.config["timeout"] = kwargs["timeout"]
        if "timeout" not in self.config:
            self.config["timeout"] = 10
        try:
            self.config["timeout"] = int(self.config["timeout"])
        except:
            self.config["timeout"] = 10

        #从参数或配置中读取retry
        if "retry" in kwargs and kwargs["retry"]:
            self.config["retry"] = kwargs["retry"]
        if "retry" not in self.config:
            self.config["retry"] = 1
        try:
            self.config["retry"] = int(self.config["retry"])
        except:
            self.config["retry"] = 1
        if self.config["retry"] <= 0:
            self.config["retry"] = 1

        #从参数或配置中读取timeout
        if "interval" in kwargs and kwargs["interval"]:
            self.config["interval"] = kwargs["interval"]
        if "interval" not in self.config:
            self.config["interval"] = 0
        try:
            self.config["interval"] = int(self.config["interval"])
        except:
            self.config["interval"] = 0
        if self.config["interval"] < 0:
            self.config["interval"] = 0

        #获取请求
        if "req" in kwargs:
            req = kwargs["req"]
        else:
            req = self.packReq()

        #重试调用do_request
        for i in range(0, self.config["retry"]):
            try:
                return self.do_request(req)
            except InterErr, e:
                if e.flag == InterErr.F_CAN_RETRY:
                    if i != self.config["retry"] - 1:
                        time.sleep(self.config["interval"])
                        continue
                    else:
                        raise
                else:
                    raise

        raise InterErr(InterErr.E_UNKNOWN, "How Can You Do This TO ME!!!!")

