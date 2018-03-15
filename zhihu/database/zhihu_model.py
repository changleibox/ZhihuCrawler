#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/2/28.

from zhihu.utils.mysql import Mysql, Model


class BaseModel(Model):
    _conn = Mysql(user='root', passwd='528515aa', db='zhihu')


class Topstory(BaseModel):
    _tbl = 'Topstory'


class Find(BaseModel):
    _tbl = 'Find'


class Topic(BaseModel):
    _tbl = 'Topic'
