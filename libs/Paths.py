#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import errno
import inspect

try:
    from . import Tools
except:
    from libs import Tools


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
    user_path = os.path.join(packages_path, 'User')
    deviot_user_path = os.path.join(user_path, 'Deviot')

    try:
        os.mkdir(deviot_user_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return deviot_user_path

# get the library user folder


def getLibraryPath():
    user_path = getDeviotUserPath()
    library_path = os.path.join(user_path, 'libraries')

    try:
        os.mkdir(library_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return library_path


def getTemplateMenuPath(file_name, user_path=False):
    if(not user_path):
        preset_path = getPresetPath()
    else:
        preset_path = getDeviotUserPath()
        preset_path = os.path.join(preset_path, 'Preset')

        try:
            os.mkdir(preset_path)
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
            os.mkdir(menu_path)
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


def getDeviotTmpPath(file_name=False):
    tmp_path = '/tmp'
    os_name = Tools.getOsName()
    if os_name == 'windows':
        tmp_path = os.environ['tmp']

    tmp_path = os.path.join(tmp_path, 'Deviot')

    if(file_name):
        tmp_path = os.path.join(tmp_path, file_name)

    try:
        os.mkdir(tmp_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

    return tmp_path
