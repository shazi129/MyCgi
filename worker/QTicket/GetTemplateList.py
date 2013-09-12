#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.template_handler import TemplateHandler

class GetTemplateList(CgiBase):
    """获取模版列表, MC使用, 查询某个产品下所有模版标题"""

    def check_data(self):
        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("typeId", "moduleId"), ())
        utils.check_dict_data(need_data, check_para)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TemplateHandler()
        ret_data = handler.get_template_list(self._proto._req["data"])
        templateList = [{"titleId":item["titleId"], "titleName":item["titleName"]}
                        for item in ret_data["templateList"]]
        self.gen_json_reply(data={"templateList":templateList})
