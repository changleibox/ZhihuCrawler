#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/2/27.
import os
import yaml


def get_configs(path_config=None):
    """获取 yaml 形式的配置文件内容.
    Note:
    + `path_config` 必须是配置文件的绝对路径
    """
    if not os.path.isabs(path_config):
        raise Exception('{0} should be absoule path.'.format(path_config))

    with open(path_config, 'r') as fp:
        configs = yaml.load(fp)

    return configs


def get_timestamp():
    import time
    return int(int(round(time.time() * 1000)))
