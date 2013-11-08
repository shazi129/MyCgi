#coding:utf-8

"""
Cauth请求格式：
{
    "version":2.0,
    "caller":"",
    "password":"",
    "callee":"cauth",
    "eventId":101,
    "timestamp":time,
    "interface":{
        "interfaceName":interface,
        "para":{}
     }
}
"""

import time
import random
import json
import ProtocolBase
from utils.net_utils import url_post
from utils.utils import check_dict_data
from utils.inter_error import InterErr

class Cauth(ProtocolBase.ProtocolBase):
    """cauth 的请求协议"""

    def __init__(self, **kargs):
        super(Cauth, self).__init__(**kargs)
        self.getConfig("cauth")

    def packReq(self):
        """打一个符合本协议的请求包"""

        request = {
            "version":2.0,
            "caller":"",
            "password":"",
            "callee":"",
            "eventId":random.randint(1, 10000),
            "timestamp":int(time.time()),
            "interface":{
                "para":{}
            }
        }

        if "version" in self.config:
            request["version"] = self.config["version"]
        if "caller" in self.config:
            request["caller"] = self.config["caller"]
        if "callee" in self.config:
            request["callee"] = self.config["callee"]
        if "password" in self.config:
            request["password"] = self.config["password"]

        if "interfaceName" in self.req:
            request["interface"]["interfaceName"] = self.req["interfaceName"]
        else:
            raise Exception("no interface name")
        if "data" in self.req:
            request["interface"]["para"] = self.req["data"]
        return request

    def do_request(self, req=None):
        """发送一个Cauth的请求"""

        if req == None:
            req = self.packReq()
        req = json.dumps(req)

        rsp = url_post(self.config["url"], req, self.config["timeout"])
        self.unpackRsp(rsp)
        if self.rsp["errno"] != 0:
            raise InterErr(InterErr.E_INTEFACE_ERR, self.rsp["errmsg"])
        return self.rsp["data"]

    def unpackRsp(self, rsp):
        """对本Cauth的回包进行处理，返回returnData"""
        try:
            rsp = json.loads(rsp)
        except Exception, e:
            raise InterErr(InterErr.E_EXINTERFACE_ERR,
                           "[%s] is not a valid cauth return" % rsp,
                           InterErr.F_CAN_RETRY)
        returnCheck = {
            "returnValue":[int],
            "returnMsg":[basestring],
            "returnData":[(list, dict)]
        }
        check_dict_data(rsp, returnCheck)
        self.rsp["errno"] = rsp["returnValue"]
        self.rsp["errmsg"] = rsp["returnMsg"]
        self.rsp["data"] = rsp["returnData"]
