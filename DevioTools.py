#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sys


def singleton(cls):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


def getOsName():
    name = sys.platform

    if name == 'win32':
        os_name = 'windows'
    elif name == 'darwin':
        os_name = 'osx'
    elif 'linux' in name:
        os_name = 'linux'
    else:
        os_name = 'other'
    return os_name


def getPythonVersion():
    python_version = sys.version_info[0]
    return python_version
