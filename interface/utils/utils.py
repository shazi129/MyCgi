#!/usr/bin/env python
#coding: utf-8

import time
import types
import traceback
from inter_error import InterErr
from log_utils import Log

def execute_cmd(cmd, **kwargs):
    """Helper method to execute command with optional retry

       :param cmd:                command will be executed
       :param process_input:      Send to opened process
       :param check_exit_code:    Single bool, int, or list of allowed
                                  exit codes.
       :preexec_fn                funtion before subprocess execute
       :param timeout             timout
       :returns: a tuple, (stdout, stderr), or None failed
    """
    process_input = kwargs.pop('process_input', None)
    check_exit_code = kwargs.pop('check_exit_code', [0])
    ignore_exit_code = True

    if isinstance(check_exit_code, bool):
        ignore_exit_code = not check_exit_code
        check_exit_code = [0]
    elif isinstance(check_exit_code, int):
        check_exit_code = [check_exit_code]
    shell = kwargs.pop('shell', True)
    timeout = int(kwargs.pop('timeout', 0))
    preexec_fn = kwargs.pop('preexec_fn', None)
    cmd = str(cmd)

    if len(kwargs):
        raise ValueError, ('Got unknown keyword args in '
                           'utils.utils.execute_cmd:%r' % kwargs)
    Log.debug('Running cmd (subprocess): %s' %cmd)

    try:
        import subprocess
        obj = subprocess.Popen(cmd, stdout     = subprocess.PIPE,
                                    stdin      = subprocess.PIPE,
                                    stderr     = subprocess.PIPE,
                                    preexec_fn = preexec_fn,
                                    shell      = shell)

        if process_input is not None:
            obj.stdin.write(process_input)
            obj.stdin.close()

        result = None
        if timeout <= 0:
            stdout = obj.stdout.read()
            stderr = obj.stderr.read()
            result = (stdout, stderr)
        else:
            used_time = 0
            wait_time = 0.5
            while used_time <= timeout:
                have_ret = obj.poll()
                if have_ret is None:
                    time.sleep(wait_time)
                    used_time += wait_time
                else:
                    stdout = obj.stdout.read()
                    stderr = obj.stderr.read()
                    result = (stdout, stderr)
                    break
            if used_time >= timeout:
                try:
                    obj.terminate()
                except AttributeError:
                    os.kill(obj.pid, 15)
                    Log.debug("PIPE.terminate is not supported")
                raise RuntimeError, 'Time out, cmd:%s' %cmd

        _returncode = obj.returncode
        Log.debug('return code was %s' %_returncode)
        if not ignore_exit_code and _returncode not in check_exit_code:
            raise RuntimeError, ("exit_code:%s, stdout:%s, stderror:%s, cmd:%s"
                      %(str(_returncode), str(result[0]), str(result[1]), cmd))
        return result
    except Exception, e:
        raise RuntimeError, 'Error in utils.utils.execute_cmd: %s' %(e)

def check_dict_data(data, param):
    """检查一个字典中的字段和字段的类型"""
    if not isinstance(data, dict) or not isinstance(param, dict):
        raise InterErr(InterErr.E_INVALID_PARA,
                "data and param must be both dict")
    for key in param:
        #key不存在的情况
        if key not in data:
            raise InterErr(InterErr.E_KEY_UNEXIST,
                    "key[%s] does not exist" % key)
        value = data[key]
        if not isinstance(param[key], (list, tuple)):
            raise InterErr(InterErr.E_INVALID_PARA,
                    "param[%s] must be a list" % key)

        for item in param[key]:
            #判断是否是特定类型, 元组默认都是类型
            if types.TypeType == type(item) or types.TupleType == type(item):
                if not isinstance(value, item):
                    raise InterErr(InterErr.E_INVALID_PARA,
                            "data[%s] is not a %s" % (key, item))
            #使用回调函数判断
            elif types.FunctionType == type(item):
                if not item(value):
                    raise InterErr(InterErr.E_INVALID_PARA,
                            "data[%s] is invalid" % (key))
            #不能识别，正确
            else:
                pass

def list_to_dict(lists, index):
    """
        将一个list改组为dict, 把key相同的放到一个列表里
        示例:[(key1, b, c), (key2, e, f), (key1, x, y)]
        --> {key1:[(b, c), (x, y)], key2:[e, f]}
        list: 一个有key的列表的列表
        index: 列表key的位置
    """
    lists = [(item[index], item[:index] + item[index+1:]) for item in lists]
    ret = {}
    for item in lists:
        if item[0] in ret:
            ret[item[0]].append(item[1])
        else:
            ret[item[0]] = [item[1]]
    return ret

def isNotEmpty(para):
    if not para or len(para) == 0:
        return False
    if isinstance(para, basestring) and len(para.strip()) == 0:
        return False
    return True

isPositive = lambda x: isinstance(x, int) and x > 0


if __name__ == "__main__":
    data = {"name":"   ", "age":27}
    check_dict_data(data, {"name":[basestring, isNotEmpty], "age":[int]})
