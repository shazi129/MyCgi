#!/usr/bin/env python
#coding:utf-8

from utils import utils
from cgi_base import CgiBase
from common import global_func
from common.ticket_handler import TicketHandler

class GetTicketDetail(CgiBase):
    """这个接口是给前台MC调用的"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("ticketId", "ownerUin"))
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        ticketId = self._proto._req["data"]["ticketId"]
        ownerUin = self._proto._req["data"]["ownerUin"]
        handler = TicketHandler()
        ret_data = handler.get_ticket_detail(ticketId, ownerUin)

        #去除不让MC用户看见的字段
        ret_data.pop("note", "")
        ret_data.pop("handler", "")

        #并将"已关闭"改为已结单
        if "statusId" in ret_data and ret_data["statusId"] == 4:
            from common.ticket_conf import STATUS_NAME_CFG
            ret_data["statusId"] = 2
            ret_data["statusName"] = STATUS_NAME_CFG[2]

        self.gen_json_reply(data=ret_data)
