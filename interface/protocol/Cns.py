#coding:utf-8

"""
请求格式:
{
    "interfaceName":"Interface",
    "data":{}
}
回复格式:
{
    "code":0,
    "msg":"success",
    "data":{}
}
"""

import json
from utils import utils
from utils.inter_error import InterErr
from utils.log_utils import Log
from ProtocolBase import ProtocolBase

class Cns(ProtocolBase):

    def unpackReq(self, field):
        raw_req = field.get_request()
        Log.info("query string: %s" %(str(raw_req)))
        try:
            json_req = json.loads(raw_req)
        except:
            raise InterErr(InterErr.E_PARAM_ERR, "input is not a json")

        check_param = {"interfaceName":[basestring, utils.isNotEmpty],
                       "data":[dict]}
        utils.check_dict_data(json_req, check_param)
        self.req["interfaceName"] = json_req["interfaceName"]
        self.req["data"] = json_req["data"]

    def packRsp(self, **kargs):
        return json.dumps(self.rsp)
