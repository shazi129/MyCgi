#!/usr/bin/env python
#encoding:utf-8

import cgi
import urlparse

class RequestFieldStorage(cgi.FieldStorage, object):
    """
    FieldStorage类的改写，使其具有传出请求串
    """
    def read_urlencoded(self):
        """Internal: read data in query string format."""
        qs = self.fp.read(self.length)
        if self.qs_on_post:
            qs += '&' + self.qs_on_post

        self._raw_request = qs

        self.list = []
        for key, value in urlparse.parse_qsl(qs, self.keep_blank_values,
                                            self.strict_parsing):
            self.list.append(cgi.MiniFieldStorage(key, value))
        self.skip_lines()

    def get_request(self):
        try:
            return self._raw_request
        except:
            return ""

