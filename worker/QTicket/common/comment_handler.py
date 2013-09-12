#!/usr/bin/env python
#coding:utf-8

import include
import global_func
import ticket_conf
from ticket_error import TicketError
from utils.db_client import DBClient
from status_handler import StatusHandler

class CommentHandler(object):

    def __init__(self, db_client=None):
        if db_client == None:
            self._client = DBClient(ticket_conf.DB_CFG)
        else:
            self._client = db_client
        self._table = "t_comment"

    def get_comment_list(self, ticketId):
        """根据ticketId获取该工单的评论列表"""

        cols = ["replier", "content", "modTimestamp", "commentId"]
        cond = {"select":cols, "where":[{"ticketId":ticketId}]}
        self._client.set_table(self._table)
        ret = self._client.query_condition(cond)
        for item in ret:
            item["time"] = item.pop("modTimestamp")
            item["time"] = item["time"].strftime("%Y-%m-%d %H:%M:%S")
        return ret

    def add_comment(self, ticketId, replier, content):
        """添加一条评论, 因为都是管理员操作，不考虑互斥"""

        handler = StatusHandler(db_client=self._client)
        if not handler.can_comment(ticketId):
            raise TicketError(TicketError.E_INVALID_STATUS,
                  "ticketId %s can not be commented" % (ticketId))

        insert = {"ticketId":ticketId, "replier":replier, "content":content,
                  "addTimestamp":None, "modTimestamp":None}
        self._client.set_table(self._table)
        self._client.insert_condition({"insert":insert})
        self._client.execute("select last_insert_id();")
        ret = self._client.fetchall()
        return {"commentId":ret[0][0]}

if __name__ == "__main__":
    from MySQLdb import IntegrityError
    try:
        handler = CommentHandler()
        print handler.add_comment("201212121123", "zhangwen", "ding!!")
    except IntegrityError, e:
        print e.errno


