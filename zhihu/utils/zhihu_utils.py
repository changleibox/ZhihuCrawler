#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Created by box on 2018/2/27.

import os
import utils


def get_configs():
    dir_root = os.path.dirname(os.path.abspath(__file__))
    fname_settings = os.path.join(dir_root, 'zhihu_configs.yaml')
    return utils.get_configs(fname_settings)
