#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.template_handler import TemplateHandler

class GetTypeList(CgiBase):
    """获取所有工单类型"""

    def check_data(self):
        """参数为空，不做检验"""
        pass

    def do_process(self):
        handler = TemplateHandler()
        ret_data = handler.get_type_list()
        self.gen_json_reply(data={"typeList":ret_data})
