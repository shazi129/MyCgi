#!/usr/bin/env python
#coding:utf-8

from utils import utils
from cgi_base import CgiBase
from common import global_func
from common.ticket_handler import TicketHandler

class CreateTicket(CgiBase):

    def check_data(self):
        need_data, check_param = global_func.get_check_para(
                self._proto._req["data"],
                ("ownerUin", "titleId", "postUin", "phone", "content"),
                ("attachId", "attachFile"))
        utils.check_dict_data(need_data, check_param)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TicketHandler()
        ret_data = handler.create_ticket(self._proto._req["data"])
        self.gen_json_reply(data=ret_data)
