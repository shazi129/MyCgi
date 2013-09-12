#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.ticket_handler import TicketHandler

class GetTicketClassification(CgiBase):

    def check_data(self):
        pass

    def do_process(self):
        handler = TicketHandler()
        ret_data = handler.get_classification()
        self.gen_json_reply(data={"class":ret_data})
