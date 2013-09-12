#!/usr/bin/env python
#coding:utf-8

from utils import utils
from cgi_base import CgiBase
from common import global_func
from common.ticket_handler import TicketHandler

class GetTicketDetailEx(CgiBase):
    """这个接口是给风云调用的"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("ticketId", ))
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        ticketId = self._proto._req["data"]["ticketId"]
        handler = TicketHandler()
        ret_data = handler.get_ticket_detail(ticketId)
        self.gen_json_reply(data=ret_data)
