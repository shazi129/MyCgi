#!/usr/bin/env python
#coding:utf-8

from utils.dbconn import *
from worker.QTicket.common.ticket_conf import *

def init_db():
    conn = DBconn(DB_CFG["host"], DB_CFG["port"], DB_CFG["user"],
                  DB_CFG["password"], None)
    conn.execute("show databases;")
    if (DB_CFG["db"],) not in conn.fetchall():
        print "database %s not exist, create..." % DB_CFG["db"]
        conn.execute("create database %s;" % DB_CFG["db"])
    conn.execute("use %s;" % DB_CFG["db"])

    #创建ID申请表
    create_table = ("create table if not exists t_id_alloc("
                    "module varchar(25) NOT NULL, "
                    "number int unsigned NOT NULL, "
                    "modTimestamp timestamp default current_timestamp on update current_timestamp,"
                    "PRIMARY KEY (module)) "
                    "ENGINE=InnoDB DEFAULT CHARSET=utf8;")
    print create_table
    conn.execute(create_table)
    #初始化ID申请表
    try:
        sql = "insert into t_id_alloc values('ticket', 0, null), ('attach', 0, null), ('template', 0, null);"
        conn.execute(sql)
    except Exception, e:
        print "insert init data into t_id_alloc error %s" % e

    #创建ID翻译表
    create_table = ("create table if not exists t_id_translate("
                    "id int unsigned NOT NULL, "
                    "name varchar(64) NOT NULL, "
                    "type varchar(64) NOT NULL, "
                    "PRIMARY KEY (id)) "
                    "ENGINE=InnoDB DEFAULT CHARSET=utf8;")
    print create_table
    conn.execute(create_table)

    #create talbes
    #创建模版表
    create_table = ("create table if not exists t_template("
                    "typeId int unsigned NOT NULL,"
                    "moduleId int unsigned NOT NULL,"
                    "titleId int unsigned NOT NULL,"
                    "content varchar(1024) NOT NULL,"
                    "addTimestamp timestamp default 0,"
                    "modTimestamp timestamp default 0 on update current_timestamp,"
                    "PRIMARY KEY (titleId), "
                    "foreign key(typeId) references t_id_translate(id), "
                    "foreign key(moduleId) references t_id_translate(id), "
                    "foreign key(titleId) references t_id_translate(id))"
                    "ENGINE=InnoDB DEFAULT CHARSET=utf8;")
    print create_table
    conn.execute(create_table)

    #创建附件表
    create_table = ("create table if not exists t_attachment("
                    "ownerUin varchar(20) NOT NULL,"
                    "attachId int unsigned NOT NULL,"
                    "attachFile varchar(128) , "
                    "addTimestamp timestamp default 0,"
                    "modTimestamp timestamp default 0 on update current_timestamp,"
                    "PRIMARY KEY (attachId))"
                    "ENGINE=InnoDB DEFAULT CHARSET=utf8;")
    print create_table
    conn.execute(create_table)

    #创建工单表
    create_table = ("create table if not exists t_ticket("
                    "ticketId varchar(12) NOT NULL,"
                    "ownerUin varchar(20) NOT NULL,"
                    "titleId int unsigned NOT NULL,"
                    "content varchar(4096) NOT NULL,"
                    "statusId int unsigned NOT NULL,"
                    "phone varchar(32) NOT NULL,"
                    "modUin varchar(20) NOT NULL,"
                    "modTimestamp timestamp default 0 on update current_timestamp,"
                    "postUin varchar(20) NOT NULL,"
                    "postTimestamp timestamp default 0,"
                    "reEditFlag int unsigned NOT NULL, "
                    "attachId int unsigned,"
                    "note varchar(512), "
                    "handler varchar(12), "
                    "PRIMARY KEY (ticketId),"
                    "foreign key(titleId) references t_template(titleId),"
                    "foreign key(attachId) references t_attachment(attachId) on delete set null)"
                    "ENGINE=InnoDB DEFAULT CHARSET=utf8;")
    print create_table
    conn.execute(create_table)

    #创建评论表
    create_table = ("create table if not exists t_comment("
                    "commentId int unsigned NOT NULL AUTO_INCREMENT,"
                    "ticketId varchar(12) NOT NULL,"
                    "replier varchar(25) NOT NULL, "
                    "content varchar(1024) NOT NULL, "
                    "addTimestamp timestamp default 0,"
                    "modTimestamp timestamp default 0 on update current_timestamp,"
                    "PRIMARY KEY (commentId),"
                    "foreign key(ticketId) references t_ticket(ticketId))"
                    "ENGINE=InnoDB DEFAULT CHARSET=utf8;")
    print create_table
    conn.execute(create_table)

def init_data():
    """初始化表中的数据"""

if __name__ == "__main__":
    init_db()
