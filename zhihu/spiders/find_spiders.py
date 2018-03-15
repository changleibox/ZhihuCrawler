#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/3/2.
from bs4 import BeautifulSoup

from zhihu.spiders.login_spiders import LoginSpiders


# noinspection PyMethodMayBeStatic
class FindSpiders(LoginSpiders):
    name = 'find'

    def start_logger_in_requests(self, response):
        return [self._get('https://www.zhihu.com/node/ExploreAnswerListV2', self.headers_general,
                          {'params': {"offset": 5, "type": "day"}}, self.parse_find)]

    def parse_find(self, response):
        bs_obj = BeautifulSoup(response.body, 'html.parser')
        div_objs = bs_obj.find_all('div', {'class': 'explore-feed feed-item'})
        for div_obj in div_objs:
            print div_obj.get_text('|', strip=True)
