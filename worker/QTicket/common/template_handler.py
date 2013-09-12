#!/usr/bin/env python
#coding:utf-8

import include
import global_func
import ticket_conf
from utils.db_client import DBClient
from id_translate_handler import IdTranslateHandler
from id_alloc_handler import IdAllocHandler
from ticket_error import TicketError

class TemplateHandler(object):

    def __init__(self, db_client=None):
        if db_client == None:
            self._client = DBClient(ticket_conf.DB_CFG)
        else:
            self._client = db_client
        self._table = "t_template"

    def is_exist(self, titleId):
        """判断titleId是否存在"""
        self._client.set_table(self._table)
        if self._client.get_count([{"titleId":titleId}]) > 0:
            return True
        return False

    def get_title_list_info(self, titleIdList):
        """获取一串titleId的信息
           titleIdList:[id1, id2]
           输出:{id1:{typeId, moduleId, titleId, typeName, moduleName, titleName}}
        """
        if len(titleIdList) == 0:
            return {}
        self._client.set_table(self._table)
        sql = ("select titleId, moduleId, typeId from %s where titleId in (%s)"
                % (self._table, ",".join([str(item) for item in titleIdList])))
        self._client.execute(sql)
        ret = self._client.fetchall()

        #获取所有id翻译
        idList = []
        for item in ret:
            idList.extend(item)
        handler = IdTranslateHandler(db_client=self._client)
        trans = handler.translate(idList)

        #按titleId组合
        ret_data = {}
        for item in ret:
            ret_data[item[0]] = {}
            for id_ in item:
                ret_data[item[0]].update(trans[id_])

        return ret_data

    def get_type_list(self):
        """获取所有工单类型"""
        sql = ("select distinct typeId from %s;" % (self._table))
        self._client.set_table(self._table)
        self._client.execute(sql)
        ret = self._client.fetchall()
        if len(ret) == 0:
            return []
        #翻译各种titleId
        id_list = []
        for item in ret:
            id_list.extend(item)
        handler = IdTranslateHandler(db_client=self._client)
        return sorted(handler.translate(id_list).values())

    def get_module_list(self, typeId):
        """获取工单类别下所有的产品信息"""
        sql = ("select distinct t_template.moduleId, t_id_translate.name "
               "from t_template left join t_id_translate "
               "on t_template.moduleId=t_id_translate.id "
               "where t_template.typeId=%s;" % typeId)
        self._client.set_table(self._table)
        self._client.execute(sql)
        ret = self._client.fetchall()
        if len(ret) == 0:
            raise TicketError(TicketError.E_NO_TYPEID,
                                     "no that typeId[%s]" % typeId)
        keys = ("moduleId", "moduleName")
        return [dict(zip(keys, item)) for item in ret]

    def get_template_detail(self, titleId):
        """获取某个模版标题的描述和内容"""

        cols = ["typeId", "moduleId", "titleId", "content",
                                      "addTimestamp", "modTimestamp"]
        query_cond = {"select":cols, "where":[{"titleId":titleId}]}
        self._client.set_table(self._table)
        templates = self._client.query_condition(query_cond)
        if len(templates) == 0:
            raise TicketError(TicketError.E_NO_TITLEID,
                                   "no that titleId[%s]" % titleId)
        titleInfo = templates[0]
        #转换各个时间
        titleInfo["addTimestamp"] = global_func.str_time(titleInfo["addTimestamp"])
        titleInfo["modTimestamp"] = global_func.str_time(titleInfo["modTimestamp"])
        #翻译各个ID
        handler = IdTranslateHandler(self._client)
        trans = handler.translate([titleInfo["typeId"],
                         titleInfo["moduleId"], titleInfo["titleId"]])
        for key in trans:
            titleInfo.update(trans[key])
        return titleInfo

    def create_type(self, para):
        """创建一个工单类型
           para中有titleName, moduleName, titleName, content"""

        #判断有没有一样的类型的工单, 待完善
        typeList = self.get_type_list()
        for item in typeList:
            if item["typeName"] == para["typeName"]:
                raise TicketError(TicketError.E_MULTI_TYPE,
                        "type[%s] already existed" % (item["typeName"]))
        #申请3个id
        handler  = IdAllocHandler(db_client=self._client)
        titleId  = handler.get_template_id(3)
        moduleId = titleId - 1;
        typeId   = titleId - 2;
        #插入id描述
        items = [(typeId, para["typeName"], "type"),
                 (moduleId, para["moduleName"], "module"),
                 (titleId, para["titleName"], "title")]
        handler = IdTranslateHandler(db_client=self._client)
        handler.create_items(items)
        #插入模版项
        try:
            insert = {"cols":["typeId", "moduleId", "titleId", "content", "addTimestamp", "modTimestamp"],
                      "values":[(typeId, moduleId, titleId, para["content"], None, None)]}
            self._client.set_table(self._table)
            self._client.insert_condition_ex(insert)
        except Exception, e:
            self._client.rollback()
            raise

        return {"titleId":titleId, "moduleId":moduleId, "typeId":typeId}

    def create_module(self, para):
        """在工单类型下创建一项产品, 这里貌似没考虑并发
           para的格式为:titleId, moduleName, titleName, content
        """

        #检查typeId下是否有这个moduleName
        module_list = self.get_module_list(para["typeId"])
        for item in module_list:
            if para["moduleName"] == item["moduleName"]:
                raise TicketError(TicketError.E_MULTI_MODULE,
                    "the module[%s] already existed" %(para["moduleName"]))

        #申请moduleId
        handler = IdAllocHandler(db_client=self._client)
        titleId = handler.get_template_id(2)
        moduleId = titleId - 1

        #在translater中加信息
        handler = IdTranslateHandler(db_client=self._client)
        items = [(moduleId, para["moduleName"], "module"),
                 (titleId, para["titleName"], "title")]
        handler.create_items(items)

        self._client.set_table(self._table)
        #创建对应关系时，因为没有titleId，将其默认设为moduleId
        try:
            insert = {"cols":["typeId", "moduleId", "titleId", "content", "addTimestamp", "modTimestamp"],
                      "values":[[para["typeId"], moduleId, titleId, para["content"], None, None]]}
            self._client.insert_condition_ex(insert)
            return {"titleId":titleId, "moduleId":moduleId, "typeId":para["typeId"]}
        except Exception, e:
            self._client.rollback()
            raise

    def create_title(self, typeId, moduleId, titleName, content):
        """创建一个工单模版，也没考虑并发"""

        #查看typeId moduleId是否已存在
        where =[{"typeId":typeId,  "moduleId":moduleId}]
        self._client.set_table(self._table)
        if self._client.get_count(where) == 0:
            raise TicketError(TicketError.E_MODULE_NOT_EXIST,
                                    "typeId or moduleId may not exist")

        #查看titleName是否已存在
        titleInfo = self.get_template_list({"typeId":typeId, "moduleId":moduleId})
        for item in titleInfo["templateList"]:
            if item["titleName"] == titleName:
                raise TicketError(TicketError.E_MULTI_TITLE,
                        "titleName[%s] already exsited" % (titleName))

        #申请titleId
        handler = IdAllocHandler(db_client=self._client)
        titleId = handler.get_template_id()
        #插入翻译表
        handler = IdTranslateHandler(db_client=self._client)
        handler.create_item(titleId, titleName, "title")
        #插入模版表
        try:
            insert = {"typeId":typeId, "moduleId":moduleId, "titleId":titleId,
                      "content":content, "addTimestamp":None, "modTimestamp":None}
            self._client.set_table(self._table)
            self._client.insert_condition({"insert":insert})
        except Exception, e:
            self._client.rollback()
            raise
        return titleId

    def get_template_list(self, para):
        """获取模版列表"""

        query_cond = {"select":["typeId", "moduleId", "titleId", "addTimestamp"],
                      "where":[{}]}

        #查询筛选条件
        if "typeId" in para:
            query_cond["where"][0]["typeId"] = para["typeId"]
        if "moduleId" in para:
            query_cond["where"][0]["moduleId"] = para["moduleId"]

        #生成分页语句
        query_cond["page"]={}
        if "page" in para:
            query_cond["page"]["page"] = para["page"]
        if "rows" in para:
            query_cond["page"]["rows"] = para["rows"]

        #生成排序语句
        if "orderField" in para and "order" in para:
            query_cond["order"] = {
                para["orderField"]:global_func.translateOrder(para["order"])}
        else:
            query_cond["order"] = {"typeId":"desc", "moduleId":"desc",
                                   "titleId":"desc"}

        self._client.set_table(self._table)
        count = self._client.get_count(query_cond["where"])
        if count == 0:
            return {"total":count, "templateList":[]}
        ret = self._client.query_condition(query_cond)

        id_list = []
        for item in ret:
            id_list.append(item["typeId"])
            id_list.append(item["moduleId"])
            id_list.append(item["titleId"])
            item["addTimestamp"] = item["addTimestamp"].strftime("%Y-%m-%d %H:%M:%S")

        #翻译各类id
        handler = IdTranslateHandler(db_client=self._client)
        trans = handler.translate(id_list)

        for item in ret:
            item.update(trans[item["typeId"]])
            item.update(trans[item["moduleId"]])
            item.update(trans[item["titleId"]])

        return {"total":count, "templateList":ret}

    def modTitleContent(self, para):
        """修改模版标题内容"""
        self._client.set_table(self._table)
        cond = {"update":{"content":para["content"]},
                "where":[{"titleId":para["titleId"]}]}

        if self._client.get_count(cond["where"]) == 0:
            raise TicketError(TicketError.E_NO_TITLEID,
                    "no that titleId[%s]" % (para["titleId"]))

        self._client.update_condition(cond)

    def getTitleId(self, typeId=None, moduleId=None):
        """获取titleId"""
        cond = {"select":["typeId", "moduleId", "titleId"], "where":[{}]}
        if typeId != None:
            cond["where"][0]["typeId"] = typeId
        if moduleId != None:
            cond["where"][0]["moduleId"] = moduleId
        self._client.set_table(self._table)
        return self._client.query_condition(cond)

    def delete_template(self, titleId):
        """删除一个模版"""
        self._client.set_table(self._table)
        return self._client.delete_condition([{"titleId":titleId}])

if __name__ == "__main__":
    handler = TemplateHandler()
    print handler.is_exist(10)

