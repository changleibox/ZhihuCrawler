#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/3/2.
import abc
from urllib import urlencode

from scrapy import Request, FormRequest
from scrapy_redis.spiders import RedisSpider
from scrapy.utils.python import to_bytes, is_listlike


def _urlencode(seq, enc='utf-8'):
    if seq:
        values = [(to_bytes(k, enc), to_bytes(v, enc))
                  for k, vs in seq
                  for v in (vs if is_listlike(vs) else [vs])]
        return urlencode(values, doseq=1)
    else:
        return ''


class BaseSpiders(RedisSpider):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def _get(cls, url, headers, body, callback):
        return NormalRequest(url=url, headers=headers, body=body, callback=callback)

    @classmethod
    def _put(cls, url, headers, body, callback):
        return NormalRequest(url=url, headers=headers, body=body, callback=callback, method='PUT')

    @staticmethod
    def _post(url, headers, formdata, callback):
        return FormRequest(url=url, headers=headers, formdata=formdata, callback=callback, dont_filter=True)


class NormalRequest(Request):

    def __init__(self, url, callback=None, method='GET', headers=None, body=None, cookies=None, meta=None,
                 encoding='utf-8', priority=0, dont_filter=True, errback=None, flags=None):
        if method == 'POST':
            if body:
                items = body.items() if isinstance(body, dict) else body
                querystr = _urlencode(items, encoding)
                headers.setdefault(b'Content-Type', b'application/x-www-form-urlencoded')
                body = querystr
        elif method == 'GET':
            if body:
                items = body.items() if isinstance(body, dict) else body
                querystr = _urlencode(items, encoding)
                url = url + ('&' if '?' in url else '?') + querystr
                body = None
        elif method == 'PUT':
            if body:
                items = body.items() if isinstance(body, dict) else body
                body = _urlencode(items, encoding)
        super(NormalRequest, self).__init__(url, callback, method, headers, body, cookies, meta, encoding, priority,
                                            dont_filter, errback, flags)
