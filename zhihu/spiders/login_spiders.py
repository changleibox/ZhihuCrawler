#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/3/2.
import abc
import hashlib
import hmac
import json

import os
import re

from PIL import Image
from bs4 import BeautifulSoup

from zhihu.spiders.base_spiders import BaseSpiders
from zhihu.utils import utils
from zhihu.utils.configs import *

is_logger_in = False


class LoginSpiders(BaseSpiders):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(BaseSpiders, self).__init__()
        self.headers_general = None
        self.captcha = None
        self.is_first_captcha = True
        self.response_login = None

    def parse(self, response):
        pass

    @abc.abstractmethod
    def start_logger_in_requests(self, response):
        """
        此方法将在登录成功以后被执行
        :param response: 登录返回的登录信息
        :return: None
        """
        return []

    def start_requests(self):
        login_success = is_logger_in and self.response_login
        return [self.start_logger_in_requests(self.response_login)] if login_success else [self.__index()]

    def parse_index(self, response):
        if response.status == 200:
            self.headers_general = self.__get_login_headers(response)
            self.is_first_captcha = True
            yield self.__monitor_captcha()
            yield self.__get_countrise()

    def parse_captcha_monitor(self, response):
        print '验证码判断：', response.body
        if response.status == 200:
            show_captcha = json.loads(response.body)['show_captcha']
            if show_captcha:
                yield self.__show_captcha()
            else:
                yield self.__login()

    def parse_captcha_show(self, response):
        print '验证码显示：', response.body
        if response.status == 202:
            captcha_img = json.loads(response.body)['img_base64']
            captcha_path = 'captcha.jpg'
            with open(captcha_path, 'wb') as f:
                f.write(base64.b64decode(captcha_img))
            try:
                Image.open(captcha_path).show()
            except (AttributeError, os.io.UnsupportedOperation):
                print u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath(captcha_path)
            self.captcha = raw_input('请输入验证码：' if self.is_first_captcha else '请输入正确的验证码：')
            yield self.__post_captcha()

    def parse_captcha_post(self, response):
        print '验证码提交：', response.body
        success = False
        if response.status == 201:
            success = json.loads(response.body)['success']
        if success:
            yield self.__login()
        else:
            self.is_first_captcha = False
            yield self.__show_captcha()

    def parse_login_response(self, response):
        self.response_login = response
        status = response.status
        try:
            if status == 201:
                global is_logger_in
                is_logger_in = True
                print '登录成功：', response.body
                logger_in_requests = self.start_logger_in_requests(response)
                for request in logger_in_requests:
                    yield request
            else:
                error_json_obj = json.loads(response.body)['error']
                print error_json_obj['message']
                yield self.__login()
        except (AttributeError, KeyError):
            print '登录失败：', response.body

    def __index(self):
        return self._get(URL_INDEX_REQUEST, None, None, self.parse_index)

    def __get_countrise(self):
        return self._get(URL_SUPPORTED_COUNTRISE, self.headers_general, None, None)

    def __monitor_captcha(self):
        return self._get(URL_CAPTCHA_REQUEST, self.headers_general, None, self.parse_captcha_monitor)

    def __show_captcha(self):
        return self._put(URL_CAPTCHA_REQUEST, self.headers_general, None, self.parse_captcha_show)

    def __post_captcha(self):
        datas = self.__get_captcha_datas()
        return self._post(URL_CAPTCHA_REQUEST, self.headers_general, datas, self.parse_captcha_post)

    def __login(self):
        """
        登录成功示例代码
        def parse_login(self, response):
            self.response_login = response
            status = response.status
            try:
                if status == 201:
                    print '登录成功：', response.body
                else:
                    error_json_obj = json.loads(response.body)['error']
                    print error_json_obj['message']
                    yield self.__login()
            except (AttributeError, KeyError):
                print '登录失败：', response.body
                self.parse(response)
        :return: 登录的Request
        """
        # account = raw_input('请输入账号：')
        # password = raw_input('请入密码：')
        account = raw_input('请输入账号：')
        password = raw_input('请输入密码：')
        datas = self.__get_login_datas(account=account, password=password, captcha=self.captcha)
        return self._post(URL_LOGIN_REQUEST, self.headers_general, datas, self.parse_login_response)

    def __get_captcha_datas(self):
        return {'input_text': self.captcha}

    @staticmethod
    def __get_token(response):
        # 获取token
        bs_obj = BeautifulSoup(response.body, 'html.parser')
        data = bs_obj.find('div', {'id': 'data'})
        xudid = None
        if data is not None:
            token_data_json = json.loads(data.attrs['data-state'].encode('utf-8'))['token']
            xsrf = token_data_json['xsrf'] if 'xsrf' in token_data_json else ''
            xudid = token_data_json['xUDID'] if 'xUDID' in token_data_json else ''
        else:
            cookies = response.headers.getlist('Set-Cookie')
            xsrf = re.search(r'_xsrf=(.*?);', cookies[2]).group(1)
        return xsrf, xudid

    @staticmethod
    def __get_signature(data):
        params = ''.join([
            data['grant_type'],
            data['client_id'],
            data['source'],
            data['timestamp'],
        ])
        return hmac.new('d1b964811afb40118a12068ff74a12f4', params.encode('utf-8'), hashlib.sha1).hexdigest()

    @classmethod
    def __get_login_datas(cls, account, password, captcha=None):
        # 构造登录请求参数，该请求数据是通过抓包获得
        post_data = CONFIGS['POST_DATAS'].copy()
        post_data['client_id'] = AUTHORIZATION
        post_data['timestamp'] = str(utils.get_timestamp())
        post_data['username'] = account
        post_data['password'] = str(password)
        post_data['captcha'] = '' if captcha is None else captcha
        post_data['signature'] = cls.__get_signature(post_data)
        return post_data

    @classmethod
    def __get_login_headers(cls, response):
        xsrf, xudid = cls.__get_token(response)
        login_headers = HEADERS.copy()
        login_headers['X-UDID'] = 'ADBsgjMePQ2PTiMYLWTDw7exZQQxGIwGoXU=' if xudid is None or len(xudid) == 0 else xudid
        login_headers['X-Xsrftoken'] = '3275e07a58d8b40b174a07933de0729e' if xsrf is None or len(xsrf) == 0 else xsrf
        login_headers['authorization'] = 'oauth %s' % AUTHORIZATION
        return login_headers
