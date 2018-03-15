#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/2/28.

from scrapy import cmdline


def run_zhihu():
    cmdline.execute('scrapy crawl zhihu'.split())


def run_find():
    cmdline.execute('scrapy crawl find'.split())


if __name__ == '__main__':
    run_zhihu()
