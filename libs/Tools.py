#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sys
import glob
import locale
import sublime

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


def setStatus(view, text=False, erase_time=0):
    '''
    Sets the info to show in the status bar of Sublime Text.
    This info is showing only when the working file is considered IoT

    Arguments: view {st object} -- stores many info related with ST
    '''

    if(not view):
        return

    info = []
    if isIOTFile(view) and not erase_time:
        info = __title__ + ' v' + str(__version__)
        view.set_status('_deviot_version', info)

    if(text and erase_time):
        view.set_status('_deviot_extra', text)

    if(erase_time > 0):
        def cleanStatus():
            view.erase_status('_deviot_extra')
        sublime.set_timeout(cleanStatus, erase_time)


def singleton(cls):
    """
    restricts the instantiation of a class to one object
    """
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
        if(line and "processing" not in line.lower() and
                "pioenvs" not in line.lower() and
                "took" not in line.lower()):
            str_error += line + '\n'
    return str_error


def toggleSerialMonitor(window=None):
    """
    Toggle the state of the serial monitor

    Arguments:
        window {object}
            windows to call or close the serial monitor

    """
    try:
        from .Serial import SerialMonitor
        from . import Serial
        from .Preferences import Preferences
        from .Messages import MonitorView
    except:
        from libs.Serial import SerialMonitor
        from libs import Serial
        from libs.Preferences import Preferences
        from libs.Messages import MonitorView

    monitor_module = Serial
    serial_monitor = None

    preferences = Preferences()
    serial_port = preferences.get('id_port', '')
    serial_ports = Serial.listSerialPorts()

    # create window and view if not exists
    if window is None:
        window = sublime.active_window()

    if serial_port in serial_ports:
        if serial_port in monitor_module.serials_in_use:
            serial_monitor = monitor_module.serial_monitor_dict.get(
                serial_port, None)
        if not serial_monitor:
            monitor_view = MonitorView(window, serial_port)
            serial_monitor = SerialMonitor(serial_port, monitor_view)

        if not serial_monitor.isRunning():
            serial_monitor.start()

            if serial_port not in monitor_module.serials_in_use:
                monitor_module.serials_in_use.append(serial_port)
            monitor_module.serial_monitor_dict[serial_port] = serial_monitor
        else:
            serial_monitor.stop()
            monitor_module.serials_in_use.remove(serial_port)


def sendSerialMessage(text):
    """
    Sends a text message over available the serial monitor

    Arguments:
        text {string}
            Text to send
    """
    try:
        from . import Serial
        from .Preferences import Preferences
    except:
        from libs import Serial
        from libs.Preferences import Preferences

    monitor_module = Serial

    preferences = Preferences()
    serial_port = preferences.get('id_port', '')
    if serial_port in monitor_module.serials_in_use:
        serial_monitor = monitor_module.serial_monitor_dict.get(
            serial_port, None)
        if serial_monitor and serial_monitor.isRunning():
            serial_monitor.send(text)


def closeSerialMonitors(preferences):
    try:
        from . import Serial
    except:
        from libs import Serial

    monitor_module = Serial
    in_use = monitor_module.serials_in_use

    if in_use:
        for port in in_use:
            cur_serial_monitor = monitor_module.serial_monitor_dict.get(
                port, None)
            if cur_serial_monitor:
                preferences.set('autorun_monitor', True)
                cur_serial_monitor.stop()
            monitor_module.serials_in_use.remove(port)


def getKeywords():
    try:
        from . import Paths
        from . import Keywords
    except:
        from libs import Paths
        from libs import Keywords

    keywords_dirs = []
    keywords = []

    # User Library
    user_lib_path = Paths.getUserLibraryPath()
    user_lib_path = os.path.join(user_lib_path, '*')

    # Platformio Libraries
    pio_lib_path = Paths.getPioLibrary()
    pio_lib_path = os.path.join(pio_lib_path, '*')

    # Core Paths
    pio_packages = Paths.getPioPackages()
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
                    keywords_dirs.append(lib)

    keywords_dirs += [user_lib_path, pio_lib_path]

    for path in keywords_dirs:
        sub_dirs = glob.glob(path)
        for sub_dir in sub_dirs:
            key_file = os.path.join(sub_dir, 'keywords.txt')
            if(os.path.isfile(key_file)):
                keywords.append(Keywords.KeywordsFile(key_file))
    return keywords


def createCompletions():
    try:
        from . import Paths
        from .JSONFile import JSONFile
    except:
        from libs import Paths
        from libs.JSONFile import JSONFile

    keywords = getKeywords()
    keyword_ids = []
    user_path = Paths.getDeviotUserPath()
    completion_path = os.path.join(user_path, 'Deviot.sublime-completions')

    cpp_keywords = ['define', 'error', 'include', 'elif', 'endif']
    cpp_keywords += ['ifdef', 'ifndef', 'undef', 'line', 'pragma']

    for k in keywords:
        for w in k.get_keywords():
            keyword_ids += [w.get_id() for w in k.get_keywords()]

    keyword_ids = set(keyword_ids)
    keyword_ids = [word for word in keyword_ids]

    completions_dict = {'scope': 'source.arduino'}
    completions_dict['completions'] = keyword_ids

    file = JSONFile(completion_path)
    file.setData(completions_dict)


def createSyntaxFile():
    try:
        from . import Paths
        from .JSONFile import JSONFile
    except:
        from libs import Paths
        from libs.JSONFile import JSONFile

    keywords = getKeywords()

    LITERAL1s = []
    KEYWORD1s = []
    KEYWORD2s = []
    KEYWORD3s = []

    # set keywords
    for k in keywords:
        for w in k.get_keywords():
            if 'LITERAL1' in w.get_type():
                LITERAL1s.append(w.get_id())
            if 'KEYWORD1' in w.get_type():
                KEYWORD1s.append(w.get_id())
            if 'KEYWORD2' in w.get_type():
                KEYWORD2s.append(w.get_id())
            if 'KEYWORD3' in w.get_type():
                KEYWORD3s.append(w.get_id())

    # formating
    LITERAL1s = set(LITERAL1s)
    LITERAL1s = '|'.join(LITERAL1s)
    KEYWORD1s = set(KEYWORD1s)
    KEYWORD1s = '|'.join(KEYWORD1s)
    KEYWORD2s = set(KEYWORD2s)
    KEYWORD2s = '|'.join(KEYWORD2s)
    KEYWORD3s = set(KEYWORD3s)
    KEYWORD3s = '|'.join(KEYWORD3s)

    # get sintax preset
    sintax_path = Paths.getSyntaxPath()
    sintax_file = JSONFile(sintax_path)
    sintax = sintax_file.readFile()

    # replace words in sintax file
    sintax = sintax.replace('${LITERAL1}', LITERAL1s)
    sintax = sintax.replace('${KEYWORD1}', KEYWORD1s)
    sintax = sintax.replace('${KEYWORD2}', KEYWORD2s)
    sintax = sintax.replace('${KEYWORD3}', KEYWORD3s)

    # Save File
    file_path = Paths.getTmLanguage()
    language_file = JSONFile(file_path)
    language_file.writeFile(sintax)
