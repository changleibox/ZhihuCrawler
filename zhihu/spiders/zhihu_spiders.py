#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/2/28.
#
# 禁止今日头条和悟空问答爬虫抓取知乎网站内容
# User-agent: *
# Request-rate: 1/2 # load 1 page per 2 seconds
# Crawl-delay: 10
#
# Disallow: /login
# Disallow: /logout
# Disallow: /resetpassword
# Disallow: /terms
# Disallow: /search
# Disallow: /notifications
# Disallow: /settings
# Disallow: /inbox
# Disallow: /admin_inbox
# Disallow: /*?guide*
# Disallow: /people/*
import json
from time import sleep

from bs4 import BeautifulSoup

from zhihu.items import ZhihuItem
from zhihu.spiders.login_spiders import LoginSpiders
from zhihu.utils.configs import *


# noinspection PyMethodMayBeStatic
class ZhihuSpiders(LoginSpiders):
    name = 'zhihu'

    def __init__(self):
        super(ZhihuSpiders, self).__init__()
        self.headers_topstory = None
        self.is_end = False
        self.next_page = None
        self.find_page = 0
        self.topic_offset = 0
        self._xsrf = None

    def start_logger_in_requests(self, response):
        self.headers_topstory = self.__get_topstory_headers(response)
        return [self.__get_topstory(), self.__get_finds(), self.__get_topic()]

    def parse_topstory(self, response):
        try:
            json_obj = json.loads(response.body)
            if response.status == 200:
                paging_obj = json_obj['paging']
                self.is_end = paging_obj['is_end']
                self.next_page = paging_obj['next']

                print '热门动态：', response.body

                item = ZhihuItem()
                item['data'] = json_obj['data']
                item['type'] = 0
                yield item

                if not self.is_end:
                    sleep(CRAWL_DELAY)
                    yield self.__get_topstory()
            else:
                print '获取热门动态失败：', json_obj['error']['message']
        except (AttributeError, KeyError):
            print '获取热门动态失败：', response.body

    def parse_find(self, response):
        try:
            bs_obj = BeautifulSoup(response.body, 'html.parser')
            div_objs = bs_obj.find_all('div', {'class': 'explore-feed feed-item'})
            item = ZhihuItem()
            item['data'] = list()
            item['type'] = 1
            data_offset = 0
            for div_obj in div_objs:
                data = dict()
                attr_obj = div_obj.find('div', {'class': 'zm-item-answer '})
                data['id'] = attr_obj.attrs['data-atoken']
                data['content'] = str(div_obj)
                item['data'].append(data)

                offset = div_obj.attrs['data-offset']
                if offset > data_offset:
                    data_offset = offset
            print '发现：', item['data']
            yield item

            if data_offset > self.find_page:
                self.find_page = int(data_offset)
                sleep(CRAWL_DELAY)
                yield self.__get_finds()
        except AttributeError as e:
            print '获取发现失败：', e.message

    def parse_topic(self, response):
        self._xsrf = response.xpath('//input[@name="_xsrf"]/@value').extract()[0]
        yield self.__get_topic_list()

    def parse_topic_list(self, response):
        print '话题：', response.body
        if response.status == 200:
            json_obj = json.loads(response.body)
            divs = json_obj['msg']
            if divs is not None and len(divs) > 0:
                from scrapy.selector import Selector
                selector = Selector(text=divs[-1])
                self.topic_offset = \
                    selector.xpath('//div[@class="feed-item feed-item-hook  folding"]/@data-score').extract()[0]

                item = ZhihuItem()
                item['data'] = list()
                item['type'] = 2

                for div in divs:
                    data = dict()
                    data['id'] = Selector(text=div).xpath('//a[@class="question_link"]/@data-id').extract()[0]
                    data['content'] = div
                    item['data'].append(data)
                yield item

                sleep(CRAWL_DELAY)
                yield self.__get_topic_list()

    def __get_topstory(self):
        if self.next_page is None:
            datas = self.__get_topstory_datas()
            return self._get(URL_TOPSTORY_REQUEST, self.headers_topstory, datas, self.parse_topstory)
        else:
            return self._get(self.next_page, self.headers_topstory, None, self.parse_topstory)

    def __get_finds(self):
        headers = self.__get_find_headers()
        datas = self.__get_find_datas(self.find_page)
        return self._get(URL_FIND_REQUEST, headers, datas, self.parse_find)

    def __following_question_count(self):
        headers = self.__get_topic_headers()
        return self._get(URL_FOLLOWING_QUESTION_COUNT, headers, None, None)

    def __switches(self):
        headers = self.__get_topic_headers()
        return self._get(URL_SWITCHS, headers, None, None)

    def __get_topic(self):
        headers = self.__get_topic_headers()
        return self._get('https://www.zhihu.com/topic', headers, None, self.parse_topic)

    def __get_topic_list(self):
        headers = self.__get_topic_list_headers(self._xsrf)
        datas = self.__get_topic_datas(self.topic_offset)
        return self._post(URL_TOPIC_REQUEST, headers, datas, self.parse_topic_list)

    def __get_topstory_headers(self, response):
        headers = self.headers_general.copy()
        if response is not None:
            json_obj = json.loads(response.body)
            headers['authorization'] = '%s %s' % (json_obj['token_type'], json_obj['cookie']['z_c0'])
        headers['X-API-VERSION'] = '3.0.53'
        return headers

    def __get_find_headers(self):
        headers = self.headers_general.copy()
        headers['Referer'] = 'https://www.zhihu.com/explore'
        return headers

    def __get_topic_headers(self):
        headers = self.__get_topstory_headers(self.response_login)
        headers['Referer'] = 'https://www.zhihu.com/topic'
        return headers

    def __get_topic_list_headers(self, _xsrf):
        headers = self.__get_topstory_headers(self.response_login)
        headers['Referer'] = 'https://www.zhihu.com/topic'
        headers['X-Xsrftoken'] = _xsrf
        return headers

    @classmethod
    def __get_topstory_datas(cls):
        return {
            'action_feed': 'True',
            'limit': '8',
            'action': 'down',
            'after_id': '5',
            'desktop': 'true'
        }

    @classmethod
    def __get_find_datas(cls, offset):
        return {'params': '{\"offset\":%d,\"type\":\"day\"}' % offset}

    @classmethod
    def __get_topic_datas(cls, offset=0):
        return {'method': 'next', 'params': '{\"offset\":%s,\"topic_id\":16}' % str(offset)}
