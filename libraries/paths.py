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

def getPluginName():
    """
    Get the name where the pugin is installed (package folder)
    """
    plugin_path = getPluginPath()
    return os.path.basename(plugin_path)

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

def getQuickPath():
    path = getPresetPath()
    quick_path = os.path.join(path, 'quick_panel.json')

    return quick_path

def getContextPath():
    path = getPresetPath()
    context_path = os.path.join(path, 'context_menu.json')

    return context_path

def getSyntaxPath():
    path = getPresetPath()
    syntax_path = os.path.join(path, 'template.syntax')

    return syntax_path

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

def getSystemIniPath():
    """
    Packages/User/Deviot/deviot.ini
    """
    deviot_path = getDeviotUserPath()
    system_ini_path = os.path.join(deviot_path, 'deviot.ini')
    return system_ini_path

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
    get denv path Packages/User/Deviot/penv/
    """
    plugin_user_path = getDeviotUserPath()
    env_dir = os.path.join(plugin_user_path, 'penv')

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
            vol_list.append(vol)
    return vol_list


def list_root_path():
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

def globalize(path):
    """Apply Glob
    
    List all files/folders in the given path and return
    a list with the results
    
    Arguments:
        path {str} -- folder path
    
    Returns:
        [list] -- list with all file/folder inside the path
    """
    path = os.path.join(path, '*')
    globalize = glob.glob(path)

    return globalize

def folder_explorer(path=None, callback=None, key=None, plist=None, index=-2):
    """Explore a path
    
    Using the quick panel, this fuction allows the user to select a path, it will be always
    a folder.

    When you give a path in the 'path' argument, the explorer will be open it in the
    given path. If you don't pass any path, the 'last_path' setting will be check to
    open the explorer in the last path used. If not path is found it will show the
    root path.

    Callbak is the function that is executed when the 'select current path' option is selected
    when the 'key' argument is given the callback will be called like callbak(key, path) if
    there is not key; callback(path). (The key argument is useful to work with the preferences)

    The rest of the arguments are used by the fuction and you don't need worry about it
    
    Keyword Arguments:
        path {str} -- stores the current path selected (default: {None})
        callback {function} -- callback called when a folder is selected (default: {None})
        key {str} -- key to use in the callback (default: {None})
        plist {list} -- list of path handled by the function (default: {None})
        index {number} -- index of the last selection (default: {-2})
    
    Returns:
        [function] -- callback with the selected path
    """

    if(index == -1):
        return

    # close if can't back anymore
    if(not path and index == 1):
        return

    # last path used
    if(not path):
        from .tools import get_setting
        path = get_setting('last_path', None)

    from .I18n import I18n
    _ = I18n().translate

    paths_list = []

    # recognize path
    if(path and not plist):
        index = -3
        new_path = globalize(path)
        paths_list.extend(new_path)

    # back
    if(index == 1 and path):
        plist = globalize(path)
        prev = os.path.dirname(path)
        back_list = globalize(prev)
        if(path == prev):
            index = -2
            path = None
            plist = None
        else:
            paths_list.extend(back_list)
            path = prev

    # select current
    if(index == 0):
        # store last path used
        from .tools import save_setting
        save_setting('last_path', path)

        if(not key):
            return callback(path)
        return callback(key, path)

    if(plist and index != 1):
        path = plist[index]

    path_caption = path if(path) else "0"
    paths_list.insert(0, _("select_{0}", path_caption))
    paths_list.insert(1, _("_previous"))

    # start from root
    if(index == -2):
        root_list = list_root_path()
        paths_list.extend(root_list)
    # iterate other path
    elif(index > 1):
        new_path = globalize(plist[index])
        paths_list.extend(new_path)

    from .quick_panel import quick_panel

    sublime.set_timeout(lambda: quick_panel(paths_list, lambda index: folder_explorer(path, callback, key, paths_list, index)), 0)