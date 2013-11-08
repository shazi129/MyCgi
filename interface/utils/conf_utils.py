#!/usr/bin/env python
#coding:utf-8

import os
import ConfigParser
from inter_error import InterErr

class Config(object):

    def __init__(self, path=None, name=None):
        """iniName配置文件名称"""
        if path == None:
            path = "%s/../config" % os.path.split(os.path.realpath(__file__))[0]
        if name == None:
            name = "common"

        self.config = ConfigParser.SafeConfigParser()

        iniFile = "%s/%s.ini" % (path, name)

        if iniFile not in self.config.read(iniFile):
            raise InterErr(InterErr.E_CONFIG_ERR, "read[%s] error" % iniFile)

        self.iniFile = iniFile

    def __getitem__(self, key):
        if key not in self.config.sections():
            raise InterErr(InterErr.E_CONFIG_ERR,
                              "no [%s] in %s" % (key, self.iniFile))
        value = {}
        for item in self.config.options(key):
            value[item] = self.config.get(key, item)
        return value
