#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from dbconn import *
from log_utils import Log
from utils import *

class DBClient(object):
    """
        一个mysql的client
    """
    def __init__(self, db_info, table=""):
        self._table = table

        check_dict_data(db_info, {"host":[basestring], "port":[int],
                        "user":[basestring], "password":[basestring],
                        "db":[basestring]})

        self._conn = DBconn(db_info["host"], db_info["port"], db_info["user"],
                            db_info["password"], db_info["db"])

    def set_table(self, table):
        self._table = table

    def execute(self, str_sql):
        Log.debug("exec sql[%s]" %str_sql)
        ret = self._conn.execute(str_sql)
        Log.debug("exec sql success, effect %d rows" %(ret))
        return ret

    def fetchall(self):
        return self._conn.fetchall()

    def str_table(self):
        if isinstance(self._table, basestring):
            return self._table
        else:
            return ",".join(self._table)

    def convert_value(self, value):
        """转化查询时的值，如字符串得加引号"""
        if isinstance(value, basestring):
            return "'%s'" % MySQLdb.escape_string(value)
        elif isinstance(value, (int, long, float)):
            return str(value)
        elif value == None:
            return "null"
        else:
            return value

    def query_condition(self, cond):
        """
            通过cond中的内容查询:
            cond:{"select":["col1","col2"], "where":[{k1:v1, k2:v2},{k3:v3}]}
            大括号是and，中括号是or
            返回[{col1:""}, {}]
        """
        select_parse = ""
        if "select" not in cond or len(cond["select"]) == 0:
            select_parse = "*"
        else:
            select_parse = ",".join(cond["select"])

        where_parse = ""
        if "where" in cond:
            where_parse = self.gen_where_parse(cond["where"])

        order_parse = ""
        if "order" in cond:
            order_parse = self.gen_order_parse(cond["order"])

        page_cond = ""
        if "page" in cond:
            page_cond = self.gen_page_parse(cond["page"])

        group_parse = ""
        if "group" in cond:
            group_parse = "group by %s" % cond["group"]

        sql_str = "select %s from %s %s %s %s %s;" %(select_parse, self.str_table(),
                                    where_parse, group_parse, order_parse, page_cond)
        self.execute(sql_str)
        ret = self.fetchall()

        if select_parse == "*":
            cond["select"] = ["col%d" %index for index in range(0, len(ret))]

        ret = [dict(zip(cond["select"], value)) for value in ret]
        return ret

    def get_count(self, where_cond = None):
        """
           获取符合where_cond的行数
        """
        where_parse = ""
        if where_cond != None:
           where_parse = self.gen_where_parse(where_cond)
        sql_str = ("select count(*) from %s %s;"
                             %(self.str_table(), where_parse))
        ret = self.execute(sql_str);
        ret = self.fetchall()

        return ret[0][0]

    def insert_condition(self, cond):
        """
            插入一条记录, cond:{"insert":{k1:v1, k2:v2}}
            插入成功，返回1
            插入失败，抛出异常
        """
        check_dict_data(cond, {"insert":[dict]})

        insert_values = ("%s" %(self.convert_value(v))
                                       for v in cond["insert"].values())
        sql_str = "insert into %s(%s) values(%s);" %(self.str_table(),
                ",".join(cond["insert"].keys()), ",".join(insert_values))
        return self.execute(sql_str);

    def insert_condition_ex(self, cond):
        """
        插入记录
        cond格式:{"cols":["列1", "列2"],
                  "values":[["value1", "value2"], ["value3", "value4"]]}
        """
        check_dict_data(cond, {"cols":[list], "values":[list, lambda x: len(x) > 0]})
        col_count = len(cond["cols"])

        col_parse = ""
        if col_count != 0:
            col_parse = "(%s)" % (",".join([str(item) for item in cond["cols"]]))

        val_list = []
        for row in cond["values"]:
            if col_count != 0 and len(row) != col_count:
                raise ValueError("invalid values lenght")
            val_parse = "(%s)" %(",".join([self.convert_value(item) for item in row]))
            val_list.append(val_parse)

        vals_parse = ",".join(val_list)
        sql = "insert into %s%s values%s;" % (self._table, col_parse, vals_parse)
        return self.execute(sql)


    def delete_condition(self, cond):
        """
            删除指定的行，cond:{"delete":[{k1:v1,...}, ...]}
            delete为空时会删除所有的东西
        """
        where_parse = self.gen_where_parse(cond)
        sql_str = "delete from %s %s;" %(self.str_table(), where_parse)
        return self.execute(sql_str)

    def update_condition(self, cond):
        """更新，如果数据表中没有要更新的
           cond 格式
           {
                update:{col:value}
                where:
           }
        """
        check_dict_data(cond, {"update":[dict]})
        u_l = ["%s=%s" %(key, self.convert_value(value)) for (key, value) in cond["update"].items()]
        if len(u_l) == 0:
            Log.debug("update_condition: no item to update")
            return 0
        update_parse = ",".join(u_l)

        where_parse = ""
        if "where" in cond:
            where_parse = self.gen_where_parse(cond["where"])
        sql_str = ("update %s set %s %s;"
                   %(self.str_table(), update_parse, where_parse))

        return self.execute(sql_str)

    def rollback(self):
        Log.debug("db client rollback");
        self._conn.rollback()

    def gen_where_parse(self, where_cond):
        """
            将一个where_cond转为字符串的where语句
            where_cond:[{k1:v1,...}, ...], {}中为and，[]中为or
        """
        where_parse = ""
        or_list = []
        if not isinstance(where_cond, (list, tuple)):
            raise TypeError, "invalid where condition: expect a list or tuple"

        for list_item in where_cond:
            if not isinstance(list_item, dict):
                raise TypeError, "invalid data:%r, expect:dict" %list_item

            and_list = self.gen_and_list(list_item)
            if len(and_list) > 0:
                or_list.append("(%s)" %(" and ".join(and_list)))

        if len(or_list) > 0:
            where_parse = "where %s" %(" or ".join(or_list))
        return where_parse


    def gen_and_list(self, and_dict):
        """
            将一个{k1:v1, k2:v2, k3:[v3, v4], k4:(v5, v6)}
            转为:[k1=v1, k2=v2, k3>=v3, k3<v4, k4 in (v5, v6)]
        """
        and_list = []
        for key, value in and_dict.items():
            if isinstance(value, list) and len(value) == 2:
                if value[0] != None:
                    and_list.append("%s>=%s"
                                    %(key, self.convert_value(value[0])))
                if value[1] != None:
                    and_list.append("%s<=%s"
                                    %(key, self.convert_value(value[1])))
            elif value in (None, ):
                and_list.append("%s is %s" %(key, self.convert_value(value)))
            elif isinstance(value, tuple) and len(value) > 0:
                and_list.append("%s in (%s)"
                        % (key, ",".join([self.convert_value(item) for item in value])))
            elif isinstance(value, dict):
                if "start" in value:
                    and_list.append("%s>=%s" %(key, self.convert_value(value["start"])))
                if "end" in value:
                    and_list.append("%s<=%s" %(key, self.convert_value(value["end"])))
                if "ne" in value and isinstance(value["ne"], (tuple, list)):
                    and_list.extend(["%s<>%s" % (key, self.convert_value(item))
                                                       for item in value["ne"]])
                if "like" in value:
                    like_parse = "%%%s%%" % value["like"]
                    and_list.append("%s like %s" % (key, self.convert_value(like_parse)))
            else:
                and_list.append("%s=%s" %(key, self.convert_value(value)))
        return and_list

    def gen_order_parse(self, order_cond):
        order_list = ["%s %s" %(key, order_cond[key]) for key in order_cond]
        return "order by %s" %(", ".join(order_list))

    def gen_page_parse(self, page_cond):
        """生成分页语句"""
        #没有rows，代表不分页
        if "rows" not in page_cond:
            return ""
        if "page" not in page_cond:
            page_cond["page"] = 1
        check_dict_data(page_cond, {"rows":[isPositive],
                                          "page":[isPositive]})
        start = (page_cond["page"] - 1) * page_cond["rows"]
        return "limit %d, %d" %(start, page_cond["rows"])


if __name__ == "__main__":
    client = CDBClient("t_pkg")
    #print client.connect()
    #print client.query_condition({"select":[],
    #                              "where":[{"plugin_name":"OpenCloud_QAE_RSAGENT"}]})
    where_cond = [{"name":"zhangwen", "age":26}, {"name":"tangxuan", "age":26}, {}]
    print client.gen_where_parse(where_cond)
    where_cond = [{}]
    print client.gen_where_parse(where_cond)
