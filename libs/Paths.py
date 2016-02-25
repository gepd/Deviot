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

try:
    from . import Tools
    from .Dir import Dir
except:
    from libs import Tools
    from libs.Dir import Dir

ROOT_PATH = 'System Root(/)'

current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))


# Get the path of deviot plugin

def getPluginPath():
    plugin_path = os.path.dirname(os.path.dirname(current_file))
    return plugin_path


# Get the package sublime text path

def getPackagesPath():
    plugin_path = getPluginPath()
    packages_path = os.path.dirname(plugin_path)
    return packages_path


# Get the path of the Preset folder

def getPresetPath():
    plugin_path = getPluginPath()
    preset_path = os.path.join(plugin_path, 'Preset')
    return preset_path


# Get the path of the language list

def getLanguagePath():
    plugin_path = getPluginPath()
    language_path = os.path.join(plugin_path, 'Languages')
    return language_path


# Get the path of the language list

def getLanguageList():
    preset_path = getPresetPath()
    language_list = os.path.join(preset_path, 'languages.list')
    return language_list


# Get deviot path from user folder

def getDeviotUserPath():
    packages_path = getPackagesPath()
    deviot_user_path = os.path.join(packages_path, 'User', 'Deviot')

    try:
        os.makedirs(deviot_user_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return deviot_user_path


# get platformio virtualenv path

def getEnvDir():
    plugin_user_path = getDeviotUserPath()
    env_dir = os.path.join(plugin_user_path, 'penv')

    try:
        os.makedirs(env_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return env_dir


# get platformio virtualenv bin path

def getEnvBinDir():
    env_dir = getEnvDir()
    env_bin_dir = os.path.join(
        env_dir, 'Scripts' if 'windows' in Tools.getOsName() else 'bin')

    try:
        os.makedirs(env_bin_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return env_bin_dir


# get cache path

def getCacheDir():
    plugin_user_path = getDeviotUserPath()
    cache_dir = os.path.join(plugin_user_path, '.cache')

    try:
        os.makedirs(cache_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return cache_dir


# get virtualenv tar file

def getEnvFile():
    cache_dir = getCacheDir()
    env_file = os.path.join(cache_dir, 'virtualenv.tar.gz')
    return env_file


# get the library user folder

def getLibraryPath():
    user_path = getDeviotUserPath()
    library_path = os.path.join(user_path, 'libraries')

    try:
        os.makedirs(library_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return library_path


def getPioLibrary():
    user_path = os.path.expanduser('~')
    pio_lib = os.path.join(user_path, '.platformio', 'lib')

    try:
        os.makedirs(pio_lib)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return pio_lib


def getSyntaxPath():
    preset_path = getPresetPath()
    sintax_path = os.path.join(preset_path, 'Arduino.syntax')
    return sintax_path


def getTmLanguage():
    preset_path = getPluginPath()
    tm_path = os.path.join(preset_path, 'Arduino.tmLanguage')
    return tm_path


def getPioPackages():
    user_path = os.path.expanduser('~')
    pio_lib = os.path.join(user_path, '.platformio', 'packages')
    return pio_lib


def getTemplateMenuPath(file_name, user_path=False):
    if(not user_path):
        preset_path = getPresetPath()
    else:
        preset_path = getDeviotUserPath()
        preset_path = os.path.join(preset_path, 'Preset')

        try:
            os.makedirs(preset_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise exc
            pass

    menu_path = os.path.join(preset_path, file_name)

    return menu_path


def getSublimeMenuPath(sub_folder=False, user_path=False):
    menu_path = getPluginPath()
    if(user_path):
        menu_path = getDeviotUserPath()

    if(sub_folder):
        menu_path = os.path.join(menu_path, sub_folder)

        try:
            os.makedirs(menu_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise exc
            pass

    menu_path = os.path.join(menu_path, 'Main.sublime-menu')

    return menu_path


def getPreferencesFile():
    deviot_user_path = getDeviotUserPath()
    preferences_path = os.path.join(
        deviot_user_path, 'Deviot Preferences.sublime-settings')
    return preferences_path


def getJSONFile(file_name):
    preset_path = getPresetPath()
    main_file_path = os.path.join(preset_path, file_name)
    return main_file_path


def getCurrentFilePath(view):
    window = view.window()
    views = window.views()

    if view not in views:
        view = window.active_view()

    return view.file_name()


def getCWD(file_path):
    folder_path = os.path.dirname(file_path)
    return folder_path


def getParentCWD(file_path):
    folder_path = os.path.dirname(file_path)
    parent = os.path.dirname(folder_path)
    return parent


def getFullIniPath(path):
    ini_path = os.path.join(path, 'platformio.ini')
    return ini_path


def getTempPath(file_name=False):
    tmp_path = '/tmp'
    os_name = Tools.getOsName()
    if os_name == 'windows':
        tmp_path = os.environ['tmp']

    tmp_path = os.path.join(tmp_path, 'Deviot')

    if(file_name):
        tmp_path = os.path.join(tmp_path, file_name)

    try:
        os.makedirs(tmp_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return tmp_path


def getOpenFolderPath(path):
    url = 'file://' + path
    return url


def listWinVolume():
    vol_list = []
    for label in range(67, 90):
        vol = chr(label) + ':\\'
        if os.path.isdir(vol):
            vol_list.append(vol)
    return vol_list


def listRootPath():
    root_list = []
    os_name = Tools.getOsName()
    if os_name == 'windows':
        root_list = listWinVolume()
    else:
        home_path = os.getenv('HOME')
        root_list = [home_path, ROOT_PATH]
    return root_list


def selectDir(window, index=-2, level=0, paths=None, key=None, func=None, label=None):
    if index == -1:
        return ''

    if level > 0 and index == 0:
        sel_path = paths[0].split('(')[1][:-1]
        if func:
            if key:
                func(key, sel_path)
        return

    else:
        if index == 1:
            level -= 1
        elif index > 1:
            level += 1

        if level <= 0:
            level = 0
            dir_path = '.'
            parent_path = '..'

            paths = listRootPath()

        else:
            sel_path = paths[index]
            if sel_path == ROOT_PATH:
                sel_path = '/'
            dir_path = os.path.abspath(sel_path)
            parent_path = os.path.join(dir_path, '..')

            cur_dir = Dir(dir_path)
            sub_dirs = cur_dir.listDirs()
            paths = [d.getPath() for d in sub_dirs]

        try:
            from .I18n import I18n
        except:
            from libs.I18n import I18n

        _ = I18n().translate

        paths.insert(0, parent_path)
        paths.insert(0, _('select_cur_dir_{0}', dir_path))

    sublime.set_timeout(lambda: window.show_quick_panel(
        paths, lambda index: selectDir(
            window, index, level, paths, key, func)), 5)


def getLibraryFolders():

    # Platformio Libraries
    pio_lib_path = getPioLibrary()
    pio_lib_path = os.path.join(pio_lib_path, '*')

    library_folders = [pio_lib_path]

    # Core Paths
    pio_packages = getPioPackages()
    pio_packages = os.path.join(pio_packages, '*')
    sub_dirs = glob.glob(pio_packages)
    for path in sub_dirs:
        sub_paths = glob.glob(path)
        for sub_path in sub_paths:
            sub_path = os.path.join(sub_path, '*')
            sub_path = glob.glob(sub_path)
            for core_lib in sub_path:
                if 'libraries' in core_lib:
                    lib = os.path.join(core_lib, '*')
                    library_folders.append(lib)

    return library_folders
