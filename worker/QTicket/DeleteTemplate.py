#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.template_handler import TemplateHandler

class DeleteTemplate(CgiBase):
    """删除一个模版, 转为fengyun设计~"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("titleId",), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TemplateHandler()
        handler.delete_template(self._proto._req["data"]["titleId"])
        self.gen_json_reply(data={})
