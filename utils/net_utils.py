#!/usr/bin/env python
#coding: utf-8

def is_ipv4(ipstr):
    try:
        return map(lambda x: -1<x<256,
                   map(int,ipstr.split('.'))) == [True, True, True, True]
    except:
        return False

def get_ip(ifname):
    ' 获取设备的ip '
    import socket
    import fcntl
    import struct

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                      struct.pack('256s', ifname[:15]))[20:24])


def get_local_ip():
    ' 获取本机ip '
    for dev in ('eth1', 'br1', 'xenbr11'):
        try:
            return get_ip(dev)
        except Exception, e:
            log_error("get local ip through sock error: %s" %(str(e)))
            log_debug(traceback.format_exc())

    cmd = ("ip route show table local | grep ^local | awk '{print $2}'"
           "| grep -v ^127 | egrep '^10|^172'")
    try:
        return execute_cmd(cmd)[0]
    except Exception, e:
        log_error("get local ip through cmd error: %s" %(str(e)))
        log_debug(traceback.format_exc())

def urlopen(url, post_data, headers={}, timeout=3):
    import socket
    import urllib2
    default_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        request = urllib2.Request(url, post_data, headers)
        response = urllib2.urlopen(request)
        socket.setdefaulttimeout(default_timeout)
        return response.read()
    except Exception, inst:
        socket.setdefaulttimeout(default_timeout)
        raise RuntimeError, inst

def get_subnet(ip, mask, default=""):
    """
        通过一个ip和掩码获取子网, 子网格式:192.168.1.1/24
    """
    import struct
    import socket
    try:
        tmp = struct.unpack("i", socket.inet_aton(ip))[0]
        tmp = tmp & (2 ** int(mask) -1)
        tmp = socket.inet_ntoa(struct.pack("i", tmp))
        return "%s/%s" % (tmp, mask)
    except Exception, e:
        if default != "":
            return default
        raise Exception("get_subnet error:%s" %(str(e)))

def url_post(url, data, timeout=5):
    import urllib2
    req = urllib2.Request(url, data)
    fd = urllib2.urlopen(req, None, timeout)
    data = ""
    while 1:
        recv = fd.read(1024)
        if len(recv) == 0:
            break;
        data += recv
    return data.strip()

def url_get(url, data, timeout=5):
    import urllib
    data = urllib.urlencode(data)
    url = "%s?%s" %(url, data)
    return url_post(url, {})
