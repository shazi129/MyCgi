#!/usr/bin/env python
#coding:utf-8

from utils import utils
from cgi_base import CgiBase
from common.ticket_handler import TicketHandler
from common import global_func

class HandleTicket(CgiBase):

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"],
                ("ticketId", "statusId", "handler"), ("comment", "note"))
        utils.check_dict_data(need_data,check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TicketHandler()
        ret_data = handler.handle_tikcet(self._proto._req["data"])
        self.gen_json_reply(data={})
