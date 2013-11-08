#coding:utf-8

__all__ = ["set_global", "get_global", "is_global", "delete_global"]

_global_saver = {}

def set_global(key, value):
    """设置一个全局变量"""
    _global_saver[key] = value

def get_global(key):
    """获取一个全局变量"""
    if key not in _global_saver:
        raise RuntimeError, "%s is not a global variable!" %key
    return _global_saver[key]

def is_global(key):
    """判断是否有这个全局变量"""
    if key not in _global_saver:
        return False
    else:
        return True

def delete_global(key):
    """删除一个全局变量"""
    if key in _global_saver:
        _global_saver.pop(key)
