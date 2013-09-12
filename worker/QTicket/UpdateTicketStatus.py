#!/usr/bin/env python
#coding:utf-8

from utils import utils
from cgi_base import CgiBase
from common.status_handler import StatusHandler
from common import global_func

class UpdateTicketStatus(CgiBase):

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"],
                ("ownerUin", "ticketIdList", "statusId"), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = StatusHandler()
        handler.update_status(self._proto._req["data"])
        self.gen_json_reply(data={})
