#!/usr/bin/env python
#coding:utf-8

"""
这个类是对请求的解析和回复的打包, 如果要换请求协议，直接换掉这个文件就好
请求格式:
{
    "version":1,
    "caller":"MC",
    "eventId":1234,
    "password":"password",
    "timestamp":12345689,
    "interface": {
        "interfaceName":"QTicket.GetList",
        "para":{}
    }
}
回复格式:
{
    "code":0,
    "msg":"success",
    "eventId":1234,
    "data":{}
}
"""

import json
from utils import utils
from utils.inter_error import InterErr
from utils.log_utils import Log
from protocol_base import ProtocolBase

class TicketProtocol(ProtocolBase):

    def get_json_req(self, req_json):
        """分析json请求"""
        self._req = req_json
        check_param = {"version":[int], "caller":[basestring, utils.isNotEmpty],
                       "eventId":[int], "password":[basestring, utils.isNotEmpty],
                       "timestamp":[int], "interface":[dict]}
        utils.check_dict_data(req_json, check_param)
        check_param = {"interfaceName":[basestring], "para":[dict]}
        utils.check_dict_data(req_json["interface"], check_param)

        self._req["interfaceName"] = req_json["interface"]["interfaceName"].strip()
        self._req["data"] = req_json["interface"]["para"]
        self._req["eventId"] = req_json["eventId"]

    def unpack_req(self, field):
        """根据协议从field中获取各请求字段"""
        raw_req = field.get_request()
        Log.info("query string: %s" %(str(raw_req)))
        try:
            json_req = json.loads(raw_req)
        except:
            raise InterErr(InterErr.E_PARAM_ERR, "input is not a json")
        self.get_json_req(json.loads(raw_req))

    def set_rsp(self, **kargs):
        self._rsp = {"code":0, "msg":"success", "data":{}}
        if "code" in kargs:
            self._rsp["code"] = kargs["code"]
        if "msg" in kargs:
            self._rsp["msg"] = kargs["msg"]
        if "data" in kargs:
            self._rsp["data"] = kargs["data"]

    def pack_rsp(self):
        if isinstance(self._rsp, dict):
            rsp = {"eventId": -1,
                   "code":self._rsp["code"],
                   "msg":self._rsp["msg"],
                   "data":self._rsp["data"]}
            if "eventId" in self._req:
                rsp["eventId"] = self._req["eventId"]

            return json.dumps(rsp)
        else:
            return data
