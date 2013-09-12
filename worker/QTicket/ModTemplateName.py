#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.id_translate_handler import IdTranslateHandler

class ModTemplateName(CgiBase):
    """获取模版id对应的描述, 转为fengyun设计~"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("id", "name"), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = IdTranslateHandler()
        handler.modName(self._proto._req["data"])
        self.gen_json_reply(data={})
