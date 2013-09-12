#!/usr/bin/env python
#coding:utf-8

"""
各种协议的基类
"""

class ProtocolBase(object):
    """请求协议的解析"""

    def __init__(self, **kargs):
        """构造函数"""

        self._req = kargs
        self._rsp = {}
        self._field = None

    def convert_req(self, proto):
        """以其他proto的请求来初始化"""
        self._req = copy.deepcopy(proto._req)
        return self

    def convert_rsp(self, proto):
        """以其他proto的回复来初始化"""
        self._rsp = copy.deepcopy(proto._rsp)
        return self

    def convert(self, proto):
        """以其他proto"""
        self.convert_req(proto).convert_rsq(proto)
        return self

    def set_rsp(self, **kargs):
        self._rsp = kargs

    def unpack_req(self, field):
        """
            根据协议从field中获取各请求字段, 只有在接受cgi请求的时候
            用到, 所以, 只要protocol中实现就好
        """
        pass

    def pack_req(self):
        """
            对请求重新打包, 通常用在将透传情况下，将请求重新打成符合
            其他cgi请求的协议格式
        """
        return None

    def unpack_rsp(self, rsp):
        """
            对回复解包, 通常用在将透传情况下, 将回复解析出来
        """
        pass

    def pack_rsp(self):
        """
            根据rsp_code等回复数据打包成输出的协议
        """
        return None
