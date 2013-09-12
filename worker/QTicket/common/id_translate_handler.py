#!/usr/bin/env python
#coding:utf-8

import include
import ticket_conf
from utils.db_client import DBClient
from ticket_error import TicketError

class IdTranslateHandler(object):

    def __init__(self, db_client=None):
        if db_client == None:
            self._client = DBClient(ticket_conf.DB_CFG)
        else:
            self._client = db_client
        self._table = "t_id_translate"

    def create_item(self, itemId, itemName, itemType):
        insert = {"insert":{"id":itemId, "name":itemName, "type":itemType}}
        self._client.set_table(self._table)
        self._client.insert_condition(insert)

    def create_items(self, para):
        """批量创建
           para格式:[(itemId, itemName, itemType), ...]
        """
        insert = {"cols":["id", "name", "type"], "values":para}
        self._client.set_table(self._table)
        return self._client.insert_condition_ex(insert)

    def translate(self, idList):
        """翻译一串id"""
        self._client.set_table(self._table)
        cond = {"select":["id", "name", "type"],
                "where":[{"id":tuple(idList)}]}
        ret = self._client.query_condition(cond)
        ret_data = {}
        for item in ret:
            type_name = item.pop("type")
            item["%sId" % type_name] = item.pop("id")
            item["%sName" % type_name] = item.pop("name")
            ret_data[item["%sId" % type_name]] = item
        return ret_data

    def getIdListByName(self, name, typeName):
        self._client.set_table(self._table)
        cond = {"select":["id"],
                "where":[{"type":typeName, "name":{"like":name}}]}
        ret = self._client.query_condition(cond)
        return [item["id"] for item in ret]

    def modName(self, para):
        """修改某个id对应的描述"""

        self._client.set_table(self._table)
        if self._client.get_count([{"id":para["id"]}]) == 0:
            raise TicketError(TicketError.E_NO_ID, "no that id[%s]" %(para["id"]))
        cond = {"update":{"name":para["name"]}, "where":[{"id":para["id"]}]}
        self._client.update_condition(cond)

if __name__ == "__main__":
    import config
    handler = IdTranslateHandler(config.DB_CFG)
    print handler.create_items([(100, "this is 100", "type"), (2, "this is 101", "module")])

