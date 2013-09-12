#!/usr/bin/env python
#coding:utf-8

import include
import global_func
import ticket_conf
import collections
from utils.db_client import DBClient
from template_handler import TemplateHandler
from attach_handler import AttachHandler
from comment_handler import CommentHandler
from id_alloc_handler import IdAllocHandler
from status_handler import StatusHandler
from id_translate_handler import IdTranslateHandler
from ticket_error import TicketError

class TicketHandler(object):

    def __init__(self, db_client=None):
        if db_client == None:
            self._client = DBClient(ticket_conf.DB_CFG)
        else:
            self._client = db_client
        self._table = "t_ticket"

    def get_ticket_detail(self, ticketId, ownerUin=None):
        """获取工单详情， appId可以为None"""

        cols = ["titleId", "content", "statusId", "ownerUin", "phone",
                "modUin", "modTimestamp", "postUin", "postTimestamp",
                "attachId", "ticketId", "note", "handler"]
        cond = {"ticketId":ticketId}
        if ownerUin != None:
            cond["ownerUin"] = ownerUin

        query_cond = {"select":cols, "where":[cond]}
        self._client.set_table(self._table)
        tickets = self._client.query_condition(query_cond)
        if len(tickets) == 0:
            raise TicketError(TicketError.E_NO_TICKETID, "no that ticketId")
        ticket_item = tickets[0]
        ticket_item["modTimestamp"] = global_func.str_time(ticket_item["modTimestamp"])
        ticket_item["postTimestamp"] = global_func.str_time(ticket_item["postTimestamp"])

        #翻译各个id
        handler = TemplateHandler(db_client=self._client)
        titleInfo = handler.get_title_list_info([ticket_item["titleId"]])
        ticket_item.update(titleInfo[ticket_item["titleId"]])

        #获取附件信息
        if ticket_item["attachId"] != None:
            handler = AttachHandler(db_client=self._client)
            ticket_item.update(handler.get_attach_info(ticket_item["attachId"]))

        #获取评论信息
        handler = CommentHandler(db_client=self._client)
        ticket_item["commentList"] = handler.get_comment_list(ticketId);

        #翻译状态
        handler = StatusHandler(db_client=self._client)
        ticket_item.update(handler.get_status_info(ticket_item["statusId"]))

        return ticket_item

    def create_ticket(self, para):
        """创建一项工单，para中必须存在工单中的各种字段,dict格式"""

        handler = IdAllocHandler(db_client=self._client)
        ticketId = handler.get_ticket_id();

        #titleId是否存在
        handler = TemplateHandler(db_client=self._client)
        if not handler.is_exist(para["titleId"]):
            raise TicketError(TicketError.E_NO_TICKETID,
                                   "no that ticketId[%s]" % para["titleId"])

        insert = {"ticketId":ticketId, "ownerUin":para["ownerUin"],
                  "titleId":para["titleId"], "content":para["content"],
                  "statusId":0, "phone":para["phone"], "modUin":para["postUin"],
                  "modTimestamp":None, "postUin":para["postUin"],
                  "postTimestamp":None, "reEditFlag":0}
        #如果存在上传附件
        if "attachFile" in para and "attachId" in para:
            insert["attachId"] = para["attachId"]
            handler = AttachHandler(db_client=self._client)
            handler.add_attach(para["attachId"], para["ownerUin"], para["attachFile"])

        #插入工单项
        self._client.set_table(self._table)
        try:
            self._client.insert_condition({"insert":insert})
        except Exception, e:
            self._client.rollback() #这个rollback是针对上传附件的行为
            raise

        return {"ticketId":ticketId}

    def is_exist(self, ticketId, ownerUin):
        """判断工单是否已存在"""
        self._client.set_table(self._table)
        where = [{"ticketId":ticketId, "ownerUin":ownerUin}]
        return self._client.get_count(where) > 0;

    def edit_ticket(self, para):
        """编辑工单"""

        ticketId = para.pop("ticketId")
        ownerUin = para.pop("ownerUin")

        #获取工单titleId，同时判断工单是否存在
        self._client.set_table(self._table)
        cond = {"select":["titleId"],
                "where":[{"ticketId":ticketId, "ownerUin":ownerUin}]}
        ret = self._client.query_condition(cond)
        if len(ret) == 0:
            raise TicketError(TicketError.E_NO_TICKETID,
                    "no that ticketId[%s] in Uin[%s]" % (ticketId, ownerUin))
        old_titleId = ret[0]["titleId"]

        #判断工单能否被编辑
        handler = StatusHandler(db_client=self._client)
        if not handler.can_edit(ticketId):
            raise TicketError(TicketError.E_INVALID_STATUS,
                    "ticketId[%s] can not be edited" %(ticketId))

        #对新titleId进行限制,不能编辑成不同的typeId
        if "titleId" in para:
            new_titleId = para["titleId"]
            handler = TemplateHandler(db_client=self._client)
            temp_info = handler.get_title_list_info([new_titleId, old_titleId])
            if new_titleId not in temp_info:
                raise TicketError(TicketError.E_NO_TITLEID,
                        "titleId[%s] does not exist" % new_titleId)
            if temp_info[new_titleId]["typeId"] != temp_info[old_titleId]["typeId"]:
                raise TicketError(TicketError.E_INVALID_TEMPLATE,
                        "can not change titleId[%s] to titleId[%s]: different type"
                        % (old_titleId, new_titleId))

        hasAttach = False
        #先对附件进行操作
        if "attachInfo" in para:
            hasAttach = True
            handler = AttachHandler(db_client=self._client)
            if para["attachInfo"]["op"] == 1:
                handler.del_attach(para["attachInfo"]["attachId"], ownerUin,
                                         para["attachInfo"]["attachFile"])
            elif para["attachInfo"]["op"] in (2, 3):
                handler.add_attach(para["attachInfo"]["attachId"], ownerUin,
                                   para["attachInfo"]["attachFile"])
                para["attachId"] = para["attachInfo"]["attachId"]
            else:
                raise TicketError(TicketError.E_INTEFACE_ERR, "no that file op")
            para.pop("attachInfo")

        #对工单项进行更新
        self._client.set_table(self._table)
        try:
            ret = self._client.update_condition({"update":para,
                  "where":[{"ticketId":ticketId, "ownerUin":ownerUin}]})
        except Exception, e:
            if hasAttach:
                self._client.rollback()
            raise

        return ticketId

    def get_ticket_list(self, para):

        query_cond = {"select":["titleId", "statusId", "postTimestamp",
                                "handler", "note", "phone", "ownerUin",
                                "ticketId", "modTimestamp"],
                      "where":[{}]}

        #生成一些比较确定的匹配, 生成where
        where_col = ["ticketId", "handler", "phone", "ownerUin", "statusId"]
        for key in para:
            if key in where_col:
                query_cond["where"][0][key] = para[key]

        #按时间筛选
        query_cond["where"][0]["postTimestamp"] = {}
        if "start" in para:
            query_cond["where"][0]["postTimestamp"]["start"] = "%s 00:00:00" % para["start"]
        if "end" in para:
            query_cond["where"][0]["postTimestamp"]["end"] = "%s 23:59:59" % para["end"]

        titleIdList = []
        #按typeId和moduleId筛选
        if "typeId" in para or "moduleId" in para:
            handler = TemplateHandler(db_client=self._client)
            ret = handler.getTitleId(para.pop("typeId", None),
                                             para.pop("moduleId", None))
            if len(ret) == 0:
                return {"total":0, "ticketList":[]}
            titleIdList = [item["titleId"] for item in ret]

        #以titleName模糊匹配
        if "titleId" not in para and "titleName" in para:
            handler = IdTranslateHandler(db_client=self._client)
            ret = handler.getIdListByName(para["titleName"], "title")
            if len(ret) == 0:
                return {"total":0, "ticketList":[]}
            titleIdList.extend(ret)

        if len(titleIdList) > 0:
            query_cond["where"][0]["titleId"] = tuple(titleIdList)

        #生成分页语句
        query_cond["page"]={}
        if "page" in para:
            query_cond["page"]["page"] = para["page"]
        if "rows" in para:
            query_cond["page"]["rows"] = para["rows"]

        #生成排序语句
        orderField = para.pop("orderField", "postTimestamp")
        if orderField not in query_cond["select"]:
            raise TicketError(TicketError.E_PARAM_ERR,
                            "order by %s is not supported" % orderField)
        order = para.pop("order", 0)
        query_cond["order"] = {orderField:global_func.translateOrder(order)}

        self._client.set_table(self._table)
        count = self._client.get_count(query_cond["where"])
        if count == 0:
            return {"total":count, "ticketList":[]}
        ret = self._client.query_condition(query_cond)

        #翻译状态
        handler = StatusHandler(db_client=self._client)
        titleIdList = []
        for item in ret:
            item["postTimestamp"] = global_func.str_time(item["postTimestamp"])
            item["modTimestamp"] = global_func.str_time(item["modTimestamp"])
            item.update(handler.get_status_info(item["statusId"]))
            titleIdList.append(item["titleId"])

        #翻译工单类型，产品，标题
        handler = TemplateHandler(db_client=self._client)
        trans = handler.get_title_list_info(titleIdList)
        for item in ret:
            item.update(trans[item["titleId"]])

        return {"total":count, "ticketList":ret}

    def handle_tikcet(self, para):
        """处理工单
           para:{
               ticketId, 必选
               handler, 必选
               statusId, 必选
               comment, 评论，可选
               note, 备注，可选
           }
           返回空
        """
        handler = StatusHandler(db_client=self._client)
        para["ticketIdList"] = [para["ticketId"]]
        handler.update_status(para)
        try:
            if "comment" in para:
                handler = CommentHandler(db_client=self._client)
                handler.add_comment(para["ticketId"],
                                    para["handler"], para["comment"])
        except Exception, e:
            self._client.rollback()
            raise

    def get_classification(self):
        """获取工单的分类信息, 返回示例:
            [
                {"moduleId":1,"moduleName":"云服务器",'processed':300,"waiting":5},
                {"moduleId":2,"moduleName":"NoSQL",'processed':200,"waiting":3}
            ]
        """
        #按titleId获取所有工单的分类信息
        cond = {"select":["titleId","statusId", "count(titleId)"],
                "where":[{"statusId":0}], "group":"titleId"}
        self._client.set_table(self._table)
        ret = self._client.query_condition(cond)
        cond = {"select":["titleId", "statusId",  "count(titleId)"],
                "where":[{"statusId":[1, None]}], "group":"titleId"}
        ret.extend(self._client.query_condition(cond))

        #提取所有titleId
        id_list = [item["titleId"] for item in ret]

        #查找这些titleId对应的产品
        handler = TemplateHandler(db_client=self._client)
        title_info = handler.get_title_list_info(id_list)

        ret_data = {}
        for item in ret:
            info = title_info[item["titleId"]]
            if info["moduleId"] not in ret_data:
                ret_data[info["moduleId"]] = {
                    "moduleId":info["moduleId"],
                    "moduleName":info["moduleName"],
                    "processed":0, "waiting":0}
            if item["statusId"] == 0:
                ret_data[info["moduleId"]]["waiting"] += item["count(titleId)"]
            else:
                ret_data[info["moduleId"]]["processed"] += item["count(titleId)"]

        return ret_data.values()

    def get_statistics(self, start, end):
        """获取工单在start,end之间的统计关系,返回示例:
        {
            "typeStatistic":{"商务类":2, "运维类":23},
            "opStatistic": {"已处理": 50, "未处理":50},
            "timeStatistic":{"total": [{"time": "2013-07-18", "count":100},
                                        {"time": "2013-07-19", "count":200}]
            }
        }
        """
        ret_data = {}
        #获取类型统计, 获取所有类型及其对应的titleId, 然后依次计算数目
        handler = TemplateHandler(db_client=self._client)
        ret = handler.get_template_list({})["templateList"]
        type_title_dict = collections.defaultdict(list)
        for item in ret:
            type_title_dict[item["typeName"]].append(item["titleId"])
        self._client.set_table(self._table)
        for item in type_title_dict:
            if len(item) == 0:
                type_title_dict[item] = 0
                continue
            count = self._client.get_count([{
                    "titleId":tuple(type_title_dict[item]),
                    "postTimestamp":{"start":start, "end":end}}])
            type_title_dict[item] = count
        ret_data["typeStatistic"] = type_title_dict

        #获取操作统计
        w_count = self._client.get_count([{
                "statusId":0,
                "postTimestamp":{"start":start, "end":end}}])
        p_count = self._client.get_count([{
                "statusId":(1, 2, 3, 4),
                "postTimestamp":{"start":start, "end":end}}])
        ret_data["opStatistic"] = {"未处理":w_count, "已处理":p_count}

        #获取时间统计
        sql = ("select DATE_FORMAT(postTimestamp, '%%Y-%%m-%%d'), count(*) from %s "
               "where postTimestamp>='%s' and postTimestamp<='%s' "
               "group by DATE_FORMAT(postTimestamp, '%%Y-%%m-%%d') "
               "order by postTimestamp asc;" % (self._table, start, end))
        ret = self._client.execute(sql)
        ret = self._client.fetchall()
        total = [dict(zip(("time", "count"), item)) for item in ret]
        ret_data["timeStatistic"] = {"total":total}

        return ret_data

if __name__ == "__main__":
    import config
    handler = TicketHandler()
    print handler.get_ticket_list({"ownerUin":"332189413", "titleName":"asdf"})


