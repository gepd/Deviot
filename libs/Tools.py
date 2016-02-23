#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import re
import sys
import glob
import locale
import sublime

try:
    from . import __version__, __title__
except:
    import __version__
    import __title__

H_EXTS = ['.h']
include = r'^\s*#include\s*[<"](\S+)[">]'


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


def setStatus(view, text=False, erase_time=0, key=False):
    '''
    Sets the info to show in the status bar of Sublime Text.
    This info is showing only when the working file is considered IoT

    Arguments: view {st object} -- stores many info related with ST
    '''

    if(not view):
        return

    is_iot = isIOTFile(view)

    if(key and is_iot):
        view.set_status(key, text)

    info = []
    if(is_iot and not erase_time):
        info = __title__ + ' v' + str(__version__)
        view.set_status('_deviot_version', info)

    if(text and erase_time):
        view.set_status('_deviot_extra', text)

    if(erase_time > 0):
        def cleanStatus():
            view.erase_status('_deviot_extra')
        sublime.set_timeout(cleanStatus, erase_time)


def userPreferencesStatus(view):
    '''
    Shows the COM port and the environment selected for the user

    Arguments: view {st object} -- stores many info related with ST
    '''
    try:
        from .Preferences import Preferences
    except:
        from libs.Preferences import Preferences
    pass
    native = Preferences().get('native', False)

    # Check for environment
    if native:
        env = Preferences().get('native_env_selected', False)
    else:
        env = Preferences().get('env_selected', False)
    if env:
        setStatus(view, env.upper(), key='_deviot_env')

    # check for port
    env = Preferences().get('id_port', False)
    if env:
        setStatus(view, env, key='_deviot_port')


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

def getDefaultPaths():
    if(getOsName() == 'windows'):
        default_path = ["C:\Python27\\", "C:\Python27\Scripts"]
    else:
        default_path = ["/usr/bin", "/usr/local/bin"]
    return default_path

def getHeaders():
    user_agent = 'Deviot/1.0.0 (Sublime-Text/3103)'
    headers = {'User-Agent': user_agent}
    return headers


def extract_tar(tar_path, extract_path='.'):
    import tarfile
    tar = tarfile.open(tar_path, 'r:gz')
    for item in tar:
        tar.extract(item, extract_path)


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
    """
    Closes all the serial monitor running

    Arguments:
        preferences {object} -- User preferences instance
    """
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


try:
    from . import Keywords
except:
    from libs import Keywords


def getKeywords():
    """
    Gets the keywords from the installed libraries

    Returns:
        [list] -- list of object with the keywords
    """
    try:
        from . import Paths
    except:
        from libs import Paths

    keywords = []
    keywords_dirs = Paths.getLibraryFolders()

    for path in keywords_dirs:
        sub_dirs = glob.glob(path)
        for sub_dir in sub_dirs:
            key_file = os.path.join(sub_dir, 'keywords.txt')
            if(os.path.isfile(key_file)):
                keywords.append(Keywords.KeywordsFile(key_file))
    return keywords


def createCompletions():
    """
    Generate the completions file
    """
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

    completions_dict = {'scope': 'source.iot'}
    completions_dict['completions'] = keyword_ids

    file = JSONFile(completion_path)
    file.setData(completions_dict)


def createSyntaxFile():
    """
    Generate the syntax file based in the installed libraries
    """
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


def addLibraryToSketch(view, edit, lib_path):
    """
    Search the file in the given path and adds as a library header

    Arguments:
        view {object} -- ST view
        edit {object} -- ST object
        lib_path {string} -- path where library is located
    """
    lib_src = os.path.join(lib_path, 'src')
    if os.path.isdir(lib_src):
        lib_path = lib_src
    lib_path = os.path.join(lib_path, '*')

    region = sublime.Region(0, view.size())
    src_text = view.substr(region)
    headers = list_headers_from_src(src_text)

    h_files = []
    sub_files = glob.glob(lib_path)
    for file in sub_files:
        file_name = os.path.basename(file)
        if H_EXTS[0] in file_name:
            h_files.append(file_name)

    h_files = [f for f in h_files if f not in headers]

    includes = ['#include <%s>' % f for f in h_files]
    text = '\n'.join(includes)
    if text:
        text += '\n'

    position = view.find('#include', 0).a
    position = (position if position != -1 else 0)

    view.insert(edit, position, text)


def list_headers_from_src(src_text):
    """
    Gets the library header(s)  already included in the sketch

    Arguments:
        src_text {string} -- text string with all the sketch

    Returns:
        [String] -- library header(s) already included
    """
    pattern_text = include
    pattern = re.compile(pattern_text, re.M | re.S)
    headers = pattern.findall(src_text)
    return headers


def openExample(path, window):
    """
    Opens an example file in the given path

    Arguments:
        path {string} -- example folder
        window {object} -- window st object to open the new sketch
    """
    files = os.path.join(path, '*')
    files = glob.glob(files)
    for file in files:
        if '.ino' in file:
            window.open_file(file)
