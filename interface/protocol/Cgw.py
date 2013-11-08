#coding:utf-8

"""
Cgw请求格式：
{
    "version":1,
    "componentName":"",
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

class Cgw(ProtocolBase.ProtocolBase):
    """cauth 的请求协议"""

    def __init__(self, **kargs):
        super(Cgw, self).__init__(**kargs)
        self.getConfig("cgw")

    def packReq(self):
        """打一个符合本协议的请求包"""

        request = {
            "version":1,
            "componentName":"",
            "eventId":random.randint(1, 10000),
            "timestamp":int(time.time()),
            "interface":{
                "para":{}
            }
        }

        if "version" in self.config:
            request["version"] = self.config["version"]
        if "componentName" in self.config:
            request["componentName"] = self.config["componentName"]

        if "interfaceName" in self.req:
            request["interface"]["interfaceName"] = self.req["interfaceName"]
        else:
            raise InterErr(InterErr.E_PARAM_ERR, "no interface name")
        if "data" in self.req:
            request["interface"]["para"] = self.req["data"]
        return request

    def do_request(self, req):
        """发送一个Cgw的请求"""

        req = json.dumps(req)

        rsp = url_post(self.config["url"], req, self.config["timeout"])
        self.unpackRsp(rsp)
        if self.rsp["errno"] != 0:
            raise InterErr(InterErr.E_INTEFACE_ERR, self.rsp["errmsg"])
        return self.rsp["data"]

    def unpackRsp(self, rsp):
        """对本Cgw的回包进行处理，返回returnData"""

        try:
            rsp = json.loads(rsp)
        except Exception, e:
            raise InterErr(InterErr.E_EXINTERFACE_ERR,
                                    "[%s] is not a valid cgw return" % rsp)

        returnCheck = {
            "returnValue":[int],
            "returnMessage":[basestring],
            "data":[(list, dict)]
        }
        check_dict_data(rsp, returnCheck)
        self.rsp["errno"] = rsp["returnValue"]
        self.rsp["errmsg"] = rsp["returnMessage"]
        self.rsp["data"] = rsp["data"]
