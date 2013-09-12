#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.ticket_handler import TicketHandler

class GetTicketStatistics(CgiBase):

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"],
                ("start", "end"), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TicketHandler()
        start = "%s 00:00:00" % self._proto._req["data"]["start"]
        end = "%s 23:59:59" % self._proto._req["data"]["end"]
        ret_data = handler.get_statistics(start, end)
        self.gen_json_reply(data=ret_data)
