#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import glob
import errno
import inspect
import sublime

ROOT_PATH = 'System Root(/)'

current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))


def getPluginPath():
    """
    Get absolute path of deviot plugin Packages/Deviot
    """
    plugin_path = os.path.dirname(os.path.dirname(current_file))
    return plugin_path


def getPackagesPath():
    """
    Get sublime text package folder
    """
    plugin_path = getPluginPath()
    packages_path = os.path.dirname(plugin_path)
    return packages_path


def getPresetPath():
    """
    Packages/Deviot/Preset
    """
    plugin_path = getPluginPath()
    preset_path = os.path.join(plugin_path, 'Preset')
    return preset_path


def getDeviotUserPath():
    """
    Deviot folder in Packages/User/Deviot/
    """
    packages_path = getPackagesPath()
    deviot_user_path = os.path.join(packages_path, 'User', 'Deviot')

    try:
        os.makedirs(deviot_user_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return deviot_user_path


def getBoardsFilePath():
    """
    Path of the file board /Packages/Deviot/boards.json
    """

    folder = getDeviotUserPath()
    file = os.path.join(folder, 'boards.json')

    return file


def getConfigFile():
    """
    config file in Packages/User/Deviot/
    """
    user_path = getDeviotUserPath()
    config_file = os.path.join(user_path, 'deviot.ini')

    return config_file


def getCacheDir():
    """
    cache folder in Packages/User/Deviot/
    """
    plugin_user_path = getDeviotUserPath()
    cache_dir = os.path.join(plugin_user_path, '.cache')

    try:
        os.makedirs(cache_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return cache_dir


def getTempPath(file_name=False):
    """
    Return the path of the temporal folder based in the O.S
    ended with Deviot (tmp/Deviot)
    if file_name argument is set it weill include in the final path
    """
    tmp_path = '/tmp'
    os_name = sublime.platform()
    if os_name == 'windows':
        tmp_path = os.environ['tmp']

    tmp_path = os.path.join(tmp_path, 'Deviot')

    if(file_name):
        tmp_path = os.path.join(tmp_path, file_name)

    return tmp_path


def getBuildPath(filename):
    from .Preferences import Preferences

    build_dir = Preferences().get('build_dir', False)

    if(build_dir):
        build_dir = os.path.join(build_dir, filename)
        return build_dir
    return getTempPath(filename)


def getEnvFile():
    """
    get virtualenv tar file in Packages/User/Deviot/.cache/
    """
    cache_dir = getCacheDir()
    env_file = os.path.join(cache_dir, 'virtualenv.tar.gz')
    return env_file


def getDenvPath():
    """
    get denv path Packages/User/Deviot/denv/
    """
    plugin_user_path = getDeviotUserPath()
    env_dir = os.path.join(plugin_user_path, 'denv')

    try:
        os.makedirs(env_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return env_dir


def getVirtualenvPath():
    """
    get virtualenv path Packages/User/Deviot/denv/virtualenv
    """

    denv = getDenvPath()
    virtualenv = os.path.join(denv, 'virtualenv')

    return virtualenv


def getEnvBinDir():
    """
    get virtualenv bin path Packages/User/Deviot/denv/virtualenv
    """
    env_dir = getDenvPath()
    env_bin_dir = os.path.join(
        env_dir, 'Scripts' if 'windows' in sublime.platform() else 'bin')

    try:
        os.makedirs(env_bin_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return env_bin_dir
