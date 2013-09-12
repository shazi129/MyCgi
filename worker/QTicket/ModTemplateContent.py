#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.template_handler import TemplateHandler

class ModTemplateContent(CgiBase):
    """获取模版id对应的描述, 转为fengyun设计~"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("titleId", "content"), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TemplateHandler()
        handler.modTitleContent(self._proto._req["data"])
        self.gen_json_reply(data={})
