#!/usr/bin/env python
#coding:utf-8

import include
import global_func
import ticket_conf
from ticket_error import TicketError
from utils.db_client import DBClient
from id_alloc_handler import IdAllocHandler

class AttachHandler(object):

    def __init__(self, db_client=None):
        if db_client == None:
            self._client = DBClient(ticket_conf.DB_CFG)
        else:
            self._client = db_client
        self._table = "t_attachment"

    def get_attach_info(self, attachId):
        cols = ["attachFile"]
        cond = {"select":cols, "where":[{"attachId":attachId}]}
        self._client.set_table(self._table)
        ret = self._client.query_condition(cond)
        if len(ret) == 0:
            raise TicketError(TicketError.E_NO_ATTACHID, "cannot find attachid: %s" % attachId)
        return ret[0]

    def add_attach(self, attachId, ownerUin, attachFile):
        """添加附件信息, 只有当有一个新申请的附件信息的时候才成功"""

        self._client.set_table(self._table)
        update = {"update":{"attachFile":attachFile,
                            "addTimestamp":None, "modTimestamp":None},
                  "where":[{"attachId":attachId, "ownerUin":ownerUin,
                            "attachFile":None, "modTimestamp":0}]}
        if not self._client.update_condition(update):
            raise TicketError(TicketError.E_NO_ATTACHID,
                    "the attachId[%s] is used or not applied" % (attachId))

    def del_attach(self, attachId, ownerUin, attachFile):
        """删除一个附件"""
        self._client.set_table(self._table)
        where = [{"attachId":attachId, "ownerUin":ownerUin, "attachFile":attachFile}]
        if not self._client.delete_condition(where):
            raise TicketError(TicketError.E_NO_ATTACHID, "can not find that attach")

    def get_attach_id(self, ownerUin):
        """获取一个附件id"""

        attachId = IdAllocHandler(db_client=self._client).get_attach_id()
        self._client.set_table(self._table)
        insert = {"insert":{"attachId":attachId, "ownerUin":ownerUin, "addTimestamp":None}}
        if not self._client.insert_condition(insert):
            raise TicketError(TicketError.E_DB_ERR, "apply attach id error")
        return attachId

if __name__ == "__main__":
    handler = AttachHandler()
    print handler.get_attach_id("332189413")


