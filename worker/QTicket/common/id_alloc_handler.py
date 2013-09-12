#!/usr/bin/env python
#coding:utf-8

import time
import include
import global_func
import ticket_conf
from utils.db_client import DBClient
from ticket_error import TicketError

class IdAllocHandler(object):

    def __init__(self, db_client=None):
        if db_client == None:
            self._client = DBClient(ticket_conf.DB_CFG)
        else:
            self._client = db_client
        self._table = "t_id_alloc"
        self._max_ticket = 10000

    def alloc_id(self, idType, num=1, idMax=None):
        """申请一个Id，idType为id的种类，num为要申请的id个数，idMax为id的最大值
        """
        self._client.set_table(self._table)
        if idMax == None:
            sql = ("update %s set number=last_insert_id(number+%s) "
                    "where module='%s'" % (self._table, num, idType))
        else:
            sql = ("update %s set number=last_insert_id((number+%s)%%%s) "
                    "where module='%s';"
                    % (self._table, num, idMax, idType))
        if not self._client.execute(sql):
            raise TicketError(TicketError.E_DB_ERR, "alloc_id error")

        self._client.execute("select last_insert_id()");
        ret = self._client.fetchall()
        return ret[0][0]

    def get_ticket_id(self, num=1):
        """为工单申请一个id，id格式:201301049999,
           前8位为日期，后4位为随机数
        """
        random_id = self.alloc_id("ticket", num, self._max_ticket)
        return "%s%04d" %(time.strftime("%Y%m%d"), random_id)

    def get_attach_id(self, num=1):
        """为附件申请一个id，纯粹的累加"""
        return self.alloc_id("attach", num)

    def get_template_id(self, num=1):
        """为模版申请一个id"""
        return self.alloc_id("template", num)


if __name__ == "__main__":
    import config
    handler = IdAllocHandler()
    print handler.get_attach_id()
