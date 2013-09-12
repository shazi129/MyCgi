#!/usr/bin/env python
#coding:utf-8

from cgi_base import CgiBase
from common import global_func
from utils import utils
from common.ticket_handler import TicketHandler

class GetTicketList(CgiBase):
    """获取工单列表"""

    def check_data(self):
        #参数转换
        if "pageSize" in self._proto._req["data"]:
            self._proto._req["data"]["rows"] = self._proto._req["data"]["pageSize"]
        if "pageNum" in self._proto._req["data"]:
            self._proto._req["data"]["page"] = self._proto._req["data"]["pageNum"]

        need_data, check_para = global_func.get_check_para(
                self._proto._req["data"], ("ownerUin",),
                ("statusId", "typeId", "moduleId", "titleId",
                 "titleName", "rows", "page", "order", "orderField"))
        utils.check_dict_data(need_data, check_para)
        if "statusId" in need_data and need_data["statusId"] == 2:
            need_data["statusId"] = (2, 4)
        self._proto._req["data"] = need_data

    def do_process(self):
        handler = TicketHandler()
        #参数转换
        ret_data = handler.get_ticket_list(self._proto._req["data"])
        ret_data["totalNum"] = ret_data.pop("total")

        #去除一些不让MC看到的参数, 并将"已关闭"改为已结单
        for item in ret_data["ticketList"]:
            item.pop("note", "")
            item.pop("handler", "")
            if item["statusId"] == 4:
                from common.ticket_conf import STATUS_NAME_CFG
                item["statusId"] = 2
                item["statusName"] = STATUS_NAME_CFG[2]

        self.gen_json_reply(data=ret_data)
