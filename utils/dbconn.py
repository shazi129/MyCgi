#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2012 Tencent.com

"""
Python模块MySQLdb的简单封装
"""

__version__ = "1.0.0"
__authors__ = ['"Li Li" <powellli@tencent.com>']

import MySQLdb


class DBconn(object):
    """ Dbconn类，封装MySQLdb中conn和cursor的操作 """

    conn = None
    cursor = None

    def __init__(self, host=None, port=None, user=None, passwd=None, db=None):
        """ 构造函数，连接数据库 """
        if host and port and user and passwd:
            self.connect(host, port, user, passwd, db)

    def __del__(self):
        """ 析构函数，关闭数据库 """
        self.close()

    def connect(self, host, port, user, passwd, db=None):
        """ 连接数据库，返回连接是否成功 """
        try:
            if db == None:
                self.conn = MySQLdb.connect(host=host, port=port, user=user,
                                            passwd=passwd, charset='utf8',
                                            use_unicode=True)
            else:
                self.conn = MySQLdb.connect(host=host, port=port, user=user,
                                            passwd=passwd, db=db, charset='utf8',
                                            use_unicode=True)
            self.cursor = self.conn.cursor()
        except Exception, e:
            self.conn = None
            self.cursor = None
            raise RuntimeError, str(e)

    def close(self):
        """ 提交操作，关闭数据库 """
        self.commit()
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def commit(self):
        """ 提交操作 """
        if self.conn is not None:
            self.conn.commit()

    def rollback(self):
        """ 回滚操作 """
        if self.conn is not None:
            self.conn.rollback()

    def insert_id(self):
        """ 获取insert后自动增长的id值 """
        if self.conn is not None:
            return self.conn.insert_id()
        else:
            return 0

    def execute(self, sql):
        """ 
        执行sql语句 
        返回一个长度为3的元组，依次为
        1. 执行结果: True/False
        2. 异常消息: 包括异常值和异常消息
        3. 影响行数: affected rows
        """
        if self.cursor is None:
            raise RuntimeError, "database connection is closed"
        return self.cursor.execute(sql)

    def gen_page_query_sql(self, query_sql, start, num):
        """
        部分查找
        """
        if query_sql.endswith(";"):
            query_sql = query_sql[0:-1]
        return "%s limit %d, %d" %(query_sql, start, num)

    def fetchall(self):
        """ 获取查询结果 """
        if self.cursor is not None:
            return self.cursor.fetchall()
        else:
            return ()
