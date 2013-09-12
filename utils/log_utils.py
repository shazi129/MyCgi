#!/usr/bin/env python
#coding: utf-8

import logging
import time
import os
import inspect

try:
    import config
    log_dir = os.path.abspath(os.path.join(config.CFG_PATH, config.LOG_CFG["dir"]))
    log_pref = config.LOG_CFG["prefix"]
    log_level = config.LOG_CFG["level"]
    log_enable = config.LOG_CFG["enable"]
    log_to_stream = config.LOG_CFG["to_stream"]
except Exception, e:
    log_dir = "./"
    log_pref = "interface"
    log_level = logging.DEBUG
    log_enable = True
    log_to_stream = True

class Logger(object):

    def __init__(self, logdir=log_dir, filename=log_pref, to_stream=log_to_stream,
                  log_level=log_level, for_others=True, log_id=0):
        self._dir = logdir
        self._filename = filename
        self._to_stream = to_stream
        self._log_level = log_level
        self._for_others = for_others
        self._log_id = log_id
        self._current_day = ""
        self._file_handler = None

        self._log_formater = logging.Formatter("[%(levelname)s]:"
            "[%(asctime)s.%(msecs)03d]:[%(process)d]:%(message)s",
             "%Y-%m-%d %H:%M:%S")
        if not os.access(logdir, os.F_OK):
            try:
                os.umask(0)
                os.mkdir(logdir)
            except Exception:
                logdir = '/tmp'

    def _create_logger(self):
        self._logger = logging.getLogger()
        self._level_dict = {
            logging.DEBUG:self._logger.debug,
            logging.INFO:self._logger.info,
            logging.WARNING:self._logger.warning,
            logging.ERROR:self._logger.error,
            logging.CRITICAL:self._logger.critical
        }
        if self._file_handler:
            self._file_handler.close()
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
            self._create_logger()

    def log(self, level, msg, *args, **kwargs):
        if not log_enable:
            return
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
        """更新log_id, 默认log_id加1"""
        if log_id != None:
            self._log_id = log_id
            return
        try:
            self._log_id = int(self._log_id)
        except:
            self._log_id = 1
        self._log_id = self._log_id + 1



class Log(object):

    logger_buffer = {
    }

    @staticmethod
    def update_id(log_id=None, module=log_pref):
        if module not in Log.logger_buffer:
            Log.logger_buffer[module] = Logger(filename=module)
        Log.logger_buffer[module].update_id(log_id)

    @staticmethod
    def info(msg, module=log_pref, *args, **kwargs):
        if module not in Log.logger_buffer:
            Log.logger_buffer[module] = Logger(filename=module)
        Log.logger_buffer[module].log(logging.INFO, msg)

    @staticmethod
    def debug(msg, module=log_pref, *args, **kwargs):
        if module not in Log.logger_buffer:
            Log.logger_buffer[module] = Logger(filename= module)
        Log.logger_buffer[module].log(logging.DEBUG, msg)

    @staticmethod
    def warning(msg, module=log_pref, *args, **kwargs):
        if module not in Log.logger_buffer:
            Log.logger_buffer[module] = Logger(filename=module)
        Log.logger_buffer[module].log(logging.WARNING, msg)

    @staticmethod
    def error(msg, module=log_pref, *args, **kwargs):
        if module not in Log.logger_buffer:
            Log.logger_buffer[module] = Logger(filename=module)
        Log.logger_buffer[module].log(logging.ERROR, msg)

    @staticmethod
    def crit(msg, module=log_pref, *args, **kwargs):
        if module not in Log.logger_buffer:
            Log.logger_buffer[module] = Logger(filename=module)
        Log.logger_buffer[module].log(logging.CRITICAL, msg)

if __name__ == "__main__":
    Log.debug("debug")
    Log.info("info")
    Log.warning("warning")
    Log.error("error")
    Log.crit("crit")
    
    while False:
        Log.info("asdfasdfasfdasdfasdf")
        time.sleep(2)
