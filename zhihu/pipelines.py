# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

from zhihu.database.zhihu_model import *
from zhihu.utils import utils


# noinspection PyUnusedLocal
class ZhihuPipeline(object):
    topstory = Topstory()
    find = Find()
    topic = Topic()

    def process_item(self, item, spider):
        item_type = item['type']
        datas = item['data']
        if item_type == 0:
            fields = ['id', 'content', 'timestamp']
            values = list()
            for topstory in datas:
                values.append((topstory['id'], json.dumps(topstory), utils.get_timestamp()))
            self.topstory.addmany_datas(fields, values, True)
        elif item_type == 1:
            fields = ['id', 'content', 'timestamp']
            values = list()
            for find in datas:
                values.append((find['id'], find['content'], utils.get_timestamp()))
            self.find.addmany_datas(fields, values, True)
        elif item_type == 2:
            fields = ['id', 'content', 'timestamp']
            values = list()
            for topic in datas:
                values.append((topic['id'], topic['content'], utils.get_timestamp()))
            self.topic.addmany_datas(fields, values, True)

        return item
