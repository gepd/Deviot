#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sys
import locale

try:
    from . import __version__, __title__
except:
    import __version__
    import __title__


def getPathFromView(view):
    """
    Gets the path of the file open in the current ST view

    Arguments: view {ST Object} -- Sublime Text Object
    """
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
    """
    Gets the name of the file from a path

    Arguments:
    path {string} -- path to extract the name
    ext {boolean} -- define if the extension is included or not (default: True)
    """
    if(not path):
        return None

    # file name with ext
    file_name = os.path.basename(path)

    # file name without ext
    if(not ext):
        file_name = os.path.splitext(file_name)[0]

    return file_name


def isIOTFile(view):
    '''
    Check if the file in the current view of ST is an allowed
    IoT file, the files are specified in the exts variable.

    Arguments:  view {st object} -- stores many info related with ST
    '''
    exts = ['ino', 'pde', 'cpp', 'c', '.S']

    file_path = getPathFromView(view)

    if file_path and file_path.split('.')[-1] in exts:
        return True
    return False


def setStatus(view):
    '''
    Sets the info to show in the status bar of Sublime Text.
    This info is showing only when the working file is considered IoT

    Arguments: view {st object} -- stores many info related with ST
    '''
    info = []

    if isIOTFile(view):

        info.append(__title__ + ' v' + str(__version__))
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
    """
    Gets the name of the S.O running in the system
    """
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
    """
    Gets the version of the python running in the system
    """
    python_version = sys.version_info[0]
    return python_version


def getSystemLang():
    """
    Get the default language in the current system
    """
    sys_language = locale.getdefaultlocale()[0]
    if not sys_language:
        sys_language = 'en'
    else:
        sys_language = sys_language.lower()
    return sys_language[:2]


def getPlatformioError(error):
    """
    Extracts descriptive error lines and removes all the
    unnecessary information

    Arguments:
        error {string} -- Full error log gets from platformIO
                          ecosystem
    """
    str_error = ""
    for line in error.split('\n'):
        if(line and "processing" not in line.lower()
            and "pioenvs" not in line.lower()
                and "took" not in line.lower()):
            str_error += line + '\n'
    return str_error
