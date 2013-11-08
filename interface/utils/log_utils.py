#!/usr/bin/env python
#coding: utf-8

import logging
import time
import os
import inspect
from conf_utils import Config

class Logger(object):

    def __init__(self, logdir="./", filename="utils", to_stream=False,
                  log_level=logging.DEBUG, for_others=True, log_id=0):
        self._dir = logdir
        self._filename = filename
        self._to_stream = to_stream
        self._log_level = log_level
        self._for_others = for_others
        self._log_id = log_id
        self._logger = logging.getLogger()
        self._level_dict = {
            logging.DEBUG:self._logger.debug,
            logging.INFO:self._logger.info,
            logging.WARNING:self._logger.warning,
            logging.ERROR:self._logger.error,
            logging.CRITICAL:self._logger.critical
        }
        self._current_day = time.strftime("%Y%m%d")
        self._log_formater = logging.Formatter("[%(levelname)s]:"
            "[%(asctime)s.%(msecs)03d]:[%(process)d]:%(message)s",
             "%Y-%m-%d %H:%M:%S")
        if not os.access(logdir, os.F_OK):
            try:
                os.umask(0)
                os.mkdir(logdir)
            except Exception:
                logdir = '/tmp'

        self._file_handler = self._get_file_handler()
        self._set_logger_format()

    def _get_file_handler(self):
        try:
            log_file = self._dir + "/" + self._filename + "_" + self._current_day + ".log"
            return logging.FileHandler(log_file)
        except Exception:
            log_file = "/tmp" + "/" + self._filename + "_" + self._current_day + ".log"
            return logging.FileHandler(log_file)

    def _set_logger_format(self):
        self._file_handler.setFormatter(self._log_formater)
        self._logger.setLevel(self._log_level)
        self._logger.addHandler(self._file_handler)
        if self._to_stream:
            streamhandler = logging.StreamHandler()
            streamhandler.setFormatter(self._log_formater)
            if (streamhandler not in self._logger.handlers
                    and len(self._logger.handlers) < 2):
                self._logger.addHandler(streamhandler)

    def _update_logger(self):
        today = time.strftime("%Y%m%d");
        if today != self._current_day:
            self._current_day = today
            self._file_handler.close()
            self._logger.handlers = []
            self._file_handler = self._get_file_handler()
            self._set_logger_format()

    def log(self, level, msg, *args, **kwargs):
        if self._for_others:
            frame_obj = inspect.currentframe().f_back.f_back
        else:
            frame_obj = inspect.currentframe().f_back
        msg_pre = "%s %s %s" %(os.path.basename(frame_obj.f_code.co_filename),
                               frame_obj.f_code.co_name, frame_obj.f_lineno)
        self._update_logger()
        self._level_dict[level]("[%s]:[%s]:%s" % (self._log_id, msg_pre, msg),
                                                              *args, **kwargs)

    def update_id(self, log_id=None):
        """"""
        if log_id != None:
            self._log_id = log_id
            return
        try:
            self._log_id = int(self._log_id)
        except:
            self._log_id = 1
        self._log_id = self._log_id + 1

class Log(object):

    logger_buffer = {}
    dir = "../"
    pref = "utils"
    enable = True
    level = logging.DEBUG

    to_stream = False

    logger_level = {
        "debug":logging.DEBUG,
        "info":logging.INFO,
        "warning":logging.WARNING,
        "error":logging.ERROR,
        "critical":logging.CRITICAL
    }

    @staticmethod
    def init(iniPath=None, iniName=None, secName="log"):
        conf = Config(path=iniPath, name=iniName)[secName]
        if "dir" in conf:
            Log.dir = "%s/%s" % (iniPath, conf["dir"])
        if "pref" in conf:
            Log.pref = conf["pref"]
        if "enable" in conf and conf["enable"] in ["false", "0"]:
            Log.enable = False
        if "to_stream" in conf and conf["to_stream"] in ["false", "0"]:
            Log.to_stream = False
        if "level" in conf and conf["level"] in Log.logger_level:
            Log.level = Log.logger_level[conf["level"]]

    @staticmethod
    def create(module):
        if module in Log.logger_buffer:
            return Log.logger_buffer[module]
        logger = Logger(logdir=Log.dir, filename=module, to_stream=Log.to_stream,
                        log_level=Log.level)
        Log.logger_buffer[module] = logger
        return logger

    @staticmethod
    def update_id(log_id=None, module=None):
        if module == None:
            module = Log.pref
        if Log.enable:
            Log.create(module).update_id(log_id)

    @staticmethod
    def info(msg, module=None, *args, **kwargs):
        if module == None:
            module = Log.pref
        if Log.enable:
            Log.create(module).log(logging.INFO, msg)

    @staticmethod
    def debug(msg, module=None, *args, **kwargs):
        if module == None:
            module = Log.pref
        if Log.enable:
            Log.create(module).log(logging.DEBUG, msg)

    @staticmethod
    def warning(msg, module=None, *args, **kwargs):
        if module == None:
            module = Log.pref
        if Log.enable:
            Log.create(module).log(logging.WARNING, msg)

    @staticmethod
    def error(msg, module=None, *args, **kwargs):
        if module == None:
            module = Log.pref
        if Log.enable:
            Log.create(module).log(logging.ERROR, msg)

    @staticmethod
    def crit(msg, module=None, *args, **kwargs):
        if module == None:
            module = Log.pref
        if Log.enable:
            Log.create(module).log(logging.CRITICAL, msg)

if __name__ == "__main__":
    Log.debug("debug")
    Log.info("info")
    Log.warning("warning")
    Log.error("error")
    Log.crit("crit")

    while True:
        Log.info("asdfasdfasfdasdfasdf")
        time.sleep(2)
