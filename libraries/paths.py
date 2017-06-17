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

def getMainMenuPath():
    """
    Packages/Deviot/Main.sublime-menu
    """
    plugin_path = getPluginPath()
    menu_path = os.path.join(plugin_path, 'Main.sublime-menu')

    return menu_path


def getPresetPath():
    """
    Packages/Deviot/presets
    """
    plugin_path = getPluginPath()
    preset_path = os.path.join(plugin_path, 'presets')
    
    return preset_path

def getLangListPath():
    path = getPresetPath()
    lang_list_path = os.path.join(path, 'languages.list')

    return lang_list_path

def getLangPath():
    path = getPluginPath()
    lang_path = os.path.join(path, 'languages')

    return lang_path


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

def getUserPioPath():
    """
    Deviot folder in Packages/User/Deviot/pio
    """
    deviot_user_path = getDeviotUserPath()
    data_path = os.path.join(deviot_user_path, 'pio')

    try:
        os.makedirs(data_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return data_path


def getPioLibrary(all=False):
    """
    ~/.platformio/lib
    """
    user_path = os.path.expanduser('~')
    pio_lib = os.path.join(user_path, '.platformio', 'lib')

    try:
        os.makedirs(pio_lib)
        os.chmod(pio_lib, 0o777)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    if(all):
        pio_lib = os.path.join(pio_lib, '*')

    return pio_lib

def getPioPackages(all=True):
    """
    ~/.platformio/packages
    """
    user_path = os.path.expanduser('~')
    pio_pack = os.path.join(user_path, '.platformio', 'packages')

    if(all):
        pio_pack = os.path.join(pio_pack, '*')

    return pio_pack


def getBoardsFileDataPath():
    """
    Deviot file in Packages/User/Deviot/pio/boards.json
    """
    user_data = getUserPioPath()
    boards_file = os.path.join(user_data, 'boards.json')

    return boards_file

def getLibrariesFileDataPath():
    """
    Deviot file in Packages/User/Deviot/pio/libraries.json
    """
    user_data = getUserPioPath()
    libraries_file = os.path.join(user_data, 'libraries.json')

    return libraries_file


def getPresetFile(file_name):
    """
    Path of the file board /Packages/Deviot/presets/filename.json
    """
    presets = getPresetPath()
    file = os.path.join(presets, file_name)

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


def listWinVolume():
    """
    return the list of system drives in windows
    """
    vol_list = []
    for label in range(67, 90):
        vol = chr(label) + ':\\'
        if os.path.isdir(vol):
            vol_list.append([vol])
    return vol_list


def listRootPath():
    """
    return the system drives in windows or unix
    """
    root_list = []
    os_name = sublime.platform()
    if os_name == 'windows':
        root_list = listWinVolume()
    else:
        home_path = os.getenv('HOME')
        root_list = [home_path, ROOT_PATH]
    return root_list


def folder_explorer(path=None, index=-2, window=None, ls=None, callback=None):
    """
    shows the list of files in the system drive(s)
    if the argument 'path' is set, it will show the
    folder in the given path. To get the selected path
    use the callback argument
    """

    if(index == -1):
        return

    if(not window):
        window = sublime.active_window()

    if(index == -2 and path):
        path = [path]

    if(index == 0 and callback):
        return callback(path[0])

    paths = []

    paths.insert(0, ['< Back'])
    paths.insert(0, ['SELECT THE CURRENT PATH'])

    # if we aren't in the root path
    if(not path and ls is not None and index > 1):
        path = ls[index]

    # list the root paths
    if(not path):
        root = listRootPath()
        paths.extend(root)

    if(index > 0):
        # when the back option is selected
        if(index == 1 and path is not None):
            dir_back = os.path.dirname(path[0])
            if(path[0] != dir_back):
                path = [dir_back]
            else:
                root = listRootPath()
                paths.extend(root)
                path = None
        else:
            # when any option (less Current and Back) is selected
            if(isinstance(path, list)):
                path = [os.path.join(path[0], ls[index][0])]

    # list the sub directories from the given path
    if(path):
        sub_paths = os.path.join(path[0], '*')
        for dirs in glob.glob(sub_paths):
            if(os.path.isdir(dirs)):
                paths.append([dirs])

    sublime.set_timeout(lambda: window.show_quick_panel(
        paths, lambda index: folder_explorer(path, index, window, paths, callback)), 0)
