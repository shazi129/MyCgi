#!/usr/bin/env python
#coding:utf-8

from utils import utils
from cgi_base import CgiBase
from common import global_func
from common.ticket_handler import TicketHandler

class EditTicket(CgiBase):

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"],
                ("ownerUin", "modUin", "ticketId"),
                ("titleId", "content", "attachInfo", "phone", "modUin"))
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TicketHandler()
        ticketId = handler.edit_ticket(self._proto._req["data"])
        self.gen_json_reply(data={"ticketId":ticketId})
