#!/usr/bin/env python
#coding:utf-8

class InterErr(Exception):
    """框架错误码"""

    E_OK                 = 0
    E_PARAM_ERR          = 1000
    E_INVALID_PARA       = 1001
    E_KEY_UNEXIST        = 1002
    E_INTEFACE_ERR       = 1003
    E_NO_INTERFACE       = 1004
    E_DB_ERR             = 1005


    def __init__(self, errno=E_INTEFACE_ERR, errmsg="interface error"):
        self.args = (errno, errmsg)
        self.errno = errno

    def __str__(self):
        return "%s" % self.args[1]

if __name__ == "__main__":
    e = InterErr()
    print e.errno
