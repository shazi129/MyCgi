#!/usr/bin/env python
#coding:utf-8

import include
import global_func
import ticket_conf
from utils.db_client import DBClient
from ticket_error import TicketError

class StatusHandler(object):

    def __init__(self, db_client=None):
        if db_client == None:
            self._client = DBClient(ticket_conf.DB_CFG)
        else:
            self._client = db_client
        self._table = "t_ticket"

    def get_status_info(self, statusId):
        """
        查询statusId对应的信息,返回{operateAuth, statusName}
        """
        try:
            return {"operateAuth":ticket_conf.STATUS_AUTH_CFG[statusId],
                    "statusName":ticket_conf.STATUS_NAME_CFG[statusId]}
        except Exception, e:
            raise TicketError(TicketError.E_INVALID_STATUS,
                    "invalid status[%s], error:%s" % (statusId, str(e)))

    def get_ticket_status(self, ticketIdList, ownerUin=None):
        """获取给定的工单的状态
           只返回存在的工单，
           如果ownerUin!=None, 只返回这个ownerUin下的
        """
        if ownerUin == None:
           where = "where"
        else:
           where = "where ownerUin='%s' and" % ownerUin
        str_sql = ("select ticketId, statusId from %s %s ticketId in (%s);"
                      % (self._table, where,  ", ".join(ticketIdList)))

        self._client.set_table(self._table)
        self._client.execute(str_sql)
        ret = self._client.fetchall()
        return dict(ret)

    def check_op(self, ticketList, newStatus, ownerUin=None):
        """检查ticketList是否都能变成newStatus状态, 返回去重的工单Id"""
        #去重，不考虑顺序
        ticketStatus = self.get_ticket_status(ticketList, ownerUin)
        ticketList = set(ticketList)
        realTicket = set(ticketStatus.keys())

        #看是否所有ticket都在
        if len(realTicket) != len(ticketList):
            raise TicketError(TicketError.E_NO_TICKETID,
                "ticketId %s dose not exsit" % (list(ticketList - realTicket)))

        #逐项对比状态权限
        for ticket in ticketStatus:
            if newStatus not in ticket_conf.STATUS_CHG_CFG[ticketStatus[ticket]]:
                raise TicketError(TicketError.E_INVALID_STATUS,
                  "ticket:%s cannot change to status:%s" % (ticket, newStatus))

        return list(ticketList)

    def can_comment(self, ticketId):
        """判断一个ticket是否能被评论：处于处理中状态"""

        status = self.get_ticket_status([ticketId])
        if len(status) == 0:
            raise TicketError(TicketError.E_NO_TICKETID,
                 "ticketId %s dose not exsit" % (ticketId))
        if status[ticketId] not in (1, 3):
            return False
        else:
            return True

    def can_edit(self, ticketId):
        """判断一个工单是否能编辑"""
        status = self.get_ticket_status([ticketId])
        if len(status) == 0:
           raise TicketError(TicketError.E_NO_TICKETID,
                   "ticketId %s dose not exsit" % (ticketId))
        if status[ticketId] not in (0, 3):
            return False
        else:
            return True


    def update_status(self, para):
        """批量更改工单状态"""

        #检查是否能更改状态
        ticketList = para["ticketIdList"]
        newStatus = para["statusId"]
        ownerUin = None
        if "ownerUin" in para:
            ownerUin = para["ownerUin"]
        ticketList = self.check_op(ticketList, newStatus, ownerUin)

        #更新状态，处理者，以及备注
        cond = {"update":{"statusId":newStatus},
                "where":[{"ticketId":tuple(ticketList)}]}
        if "handler" in para:
            cond["update"]["handler"] = para["handler"]
        if "note" in para:
            cond["update"]["note"] = para["note"]

        self._client.set_table(self._table)
        return self._client.update_condition(cond)

if __name__ == "__main__":
    handler = StatusHandler()
    print handler.get_status_info(1)
