#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sys


def getPathFromView(view):
    try:
        window = view.window()
        views = window.views()
        if view not in views:
            view = window.active_view()
    except:
        pass

    file_view = view.file_name()

    if(not file_view):
        return None

    return file_view


def getFileNameFromPath(path, ext=True):
    if(not path):
        return None

    # file name with ext
    file_name = os.path.basename(path)

    # file name without ext
    if(not ext):
        file_name = os.path.splitext(file_name)[0]

    return file_name


def isIOTFile(view):
    '''IoT File

    Check if the file in the current view of ST is an allowed
    IoT file, the files are specified in the exts variable.

    Arguments:
            view {st object} -- stores many info related with ST
    '''
    exts = ['ino', 'pde', 'cpp', 'c', '.S']

    file_path = getPathFromView(view)

    if file_path and file_path.split('.')[-1] in exts:
        return True
    return False


def setStatus(view, plugin_version=False):
    '''Status bar

    Set the info to show in the status bar of Sublime Text.
    This info is showing only when the working file is considered IoT

    Arguments:
            view {st object} -- stores many info related with ST
    '''
    info = []

    if isIOTFile(view):
        if(not plugin_version):
            plugin_version = 0

        info.append('Deviot v' + str(plugin_version))
        full_info = ' | '.join(info)

        view.set_status('Deviot', full_info)


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
