#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.template_handler import TemplateHandler

class CreateTemplateTitle(CgiBase):

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"],
                ("typeId", "moduleId", "titleName", "content"), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TemplateHandler()
        data = self._proto._req["data"]
        titleId = handler.create_title(data["typeId"], data["moduleId"],
                                       data["titleName"], data["content"])
        self.gen_json_reply(data={"titleId":titleId})
