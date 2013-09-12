#!/usr/bin/env python
#coding:utf-8

def str_time(para_time):
    try:
        return para_time.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "0000-00-00 00:00:00"

isTicketId = lambda x: x.isdigit() and len(x) == 12
isUin = lambda x: x.isdigit()
isAppId = lambda x: x > 0
isStatusId = lambda x: x in (0, 1, 2, 3, 4)
isTypeId = lambda x: x > 0
isModuleId = lambda x: x > 0
isTitleId = lambda x: x > 0
isAttachId = lambda x: x > 0
isModuleId = lambda x: x > 0

def isTicketIdList(ticketIdList):
    if not isinstance(ticketIdList, (tuple, list)):
        return False
    isList = [item for item in ticketIdList if not isTicketId(item)]
    if len(isList) > 0:
        return False
    return True

def isStatusIdList(statusIdList):
    if not isinstance(statusIdList, (tuple, list)):
        return False
    isList = [item for item in statusIdList if not isStatusId(item)]
    if len(isList) > 0:
        return False
    return True

def isAttachInfo(attachInfo):
    from utils import utils
    check_para = {"attachId":[int, isAttachId],
                  "attachFile":[basestring, utils.isNotEmpty],
                  "op":[int, lambda x: x in (1, 2, 3)]}
    try:
        utils.check_dict_data(attachInfo, check_para)
        return True
    except:
        return False

def isPhone(para):
    return True

def isDate(para):
    """看是不是1999-12-12格式的日期"""
    if not isinstance(para, basestring):
        return False
    import time
    try:
        time.strptime(para, "%Y-%m-%d")
        return True
    except:
        return False

def translateOrder(para):
    if isinstance(para, int) and para == 0:
        return "asc"
    return "desc"

def get_check_para(data, required=(), optional=()):
    from utils import utils
    check_para = {}
    need_data = {}
    total_para = {
        "start":[isDate],
        "end":[isDate],
        "ticketId":[basestring, isTicketId],
        "typeId":[int, isTypeId],
        "typeName":[basestring, utils.isNotEmpty],
        "moduleId":[int, isModuleId],
        "moduleName":[basestring, utils.isNotEmpty],
        "titleId":[int, isTitleId],
        "titleName":[basestring, utils.isNotEmpty],
        "handler":[basestring, utils.isNotEmpty],
        "ownerUin":[basestring, isUin],
        "postUin":[basestring, isUin],
        "modUin":[basestring, isUin],
        "phone":[basestring, isPhone],
        "statusId":[int, isStatusId],
        "statusIdList":[isStatusIdList],
        "moduleId":[int, isModuleId],
        "rows":[int, utils.isPositive],
        "page":[int, utils.isPositive],
        "orderField":[basestring, utils.isNotEmpty],
        "order":[int, lambda x: x in (0, 1)],
        "id":[int, lambda x: x > 0],
        "name":[basestring, utils.isNotEmpty],
        "content":[basestring, utils.isNotEmpty],
        "comment":[basestring, utils.isNotEmpty],
        "attachInfo":[dict, isAttachInfo],
        "attachId":[int, isAttachId],
        "attachFile":[basestring, utils.isNotEmpty],
        "ticketIdList":[list, isTicketIdList],
        "note":[basestring, utils.isNotEmpty],
    }

    for item in required:
        check_para[item] = total_para[item]
        if item in data:
            need_data[item] = data[item]

    for item in optional:
        if item in data:
            check_para[item] = total_para[item]
            need_data[item] = data[item]

    return need_data, check_para

if __name__ == "__main__":
    print translateOrder(3)
