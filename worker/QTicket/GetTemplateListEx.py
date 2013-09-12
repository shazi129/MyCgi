#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.template_handler import TemplateHandler

class GetTemplateListEx(CgiBase):
    """获取模版列表, 专为fengyun设计~"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], (),
                ("orderField", "order", "rows", "page"))
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TemplateHandler()
        ret_data = handler.get_template_list(self._proto._req["data"])
        self.gen_json_reply(data=ret_data)
