#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.attach_handler import AttachHandler

class GetAttachId(CgiBase):
    """生成一个attachId"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("ownerUin", ), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = AttachHandler()
        attachId = handler.get_attach_id(self._proto._req["data"]["ownerUin"])
        self.gen_json_reply(data={"attachId":attachId})
