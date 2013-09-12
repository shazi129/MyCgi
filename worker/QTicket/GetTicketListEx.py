#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.ticket_handler import TicketHandler

class GetTicketListEx(CgiBase):
    """获取工单列表, 这个接口专为风云使用"""

    def check_data(self):
        """"""
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"],(),
                ("ticketId", "handler", "ownerUin", "phone", "statusIdList",
                 "moduleId", "rows", "page", "orderField", "order",
                 "start", "end"))
        utils.check_dict_data(need_data, check_para)
        if "statusIdList" in need_data:
            need_data["statusId"] = tuple(need_data.pop("statusIdList"))

        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TicketHandler()
        ret_data = handler.get_ticket_list(self._proto._req["data"])
        self.gen_json_reply(data=ret_data)
