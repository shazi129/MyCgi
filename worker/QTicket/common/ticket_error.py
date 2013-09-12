#!/usr/bin/env python
#coding:utf-8

from utils.inter_error import InterErr

class TicketError(InterErr):
    """工单系统错误码"""

    E_NO_TICKETID        = 2100
    E_NO_TITLEID         = 2101
    E_NO_ATTACHID        = 2102
    E_NO_ID              = 2103
    E_NO_MODULEID        = 2104
    E_NO_TYPEID          = 2015

    E_INVALID_TEMPLATE   = 2201
    E_INVALID_STATUS     = 2202
    E_MULTI_MODULE       = 2203
    E_MODULE_NOT_EXIST   = 2204
    E_MULTI_TITLE        = 2205
    E_MULTI_TYPE         = 2206
