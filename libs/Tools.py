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

from . import __version__, __title__

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


def getNameFromPath(path, ext=True):
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


def isIOTFile(path):
    '''
    Check if the file in the current view of ST is an allowed
    IoT file, the files are specified in the exts variable.
    '''
    exts = ['ino', 'pde', 'cpp', 'c', '.S']

    if path and path.split('.')[-1] in exts:
        return True
    return False


def setStatus(text=False, erase_time=0, key=False):
    '''
    Sets the info to show in the status bar of Sublime Text.
    This info is showing only when the working file is considered IoT

    Arguments: view {st object} -- stores many info related with ST
    '''
    window = sublime.active_window()
    view = window.active_view()

    is_iot = isIOTFile(view.file_name())

    if(key and is_iot):
        view.set_status(key, text)

    info = []
    if(is_iot and not erase_time):

        from .Preferences import Preferences

        pio_version = Preferences().get('pio_version', 0)

        info = '%s v%s | Pio v%s' % (__title__, str(__version__), pio_version)
        view.set_status('_deviot_version', info)

    if(text and erase_time):
        view.set_status('_deviot_extra', text)

    if(erase_time > 0):
        def cleanStatus():
            view.erase_status('_deviot_extra')
        sublime.set_timeout(cleanStatus, erase_time)


def userPreferencesStatus():
    '''
    Shows the COM port and the environment selected for the user

    Arguments: view {st object} -- stores many info related with ST
    '''
    from .Preferences import Preferences

    native = Preferences().get('native', False)

    # Check for environment
    if native:
        env = Preferences().get('native_env_selected', False)
    else:
        env = Preferences().get('env_selected', False)
    if env:
        setStatus(env.upper(), key='_deviot_env')

    # check for port
    port = Preferences().get('port_bar', False)
    if port:
        setStatus(port.upper(), key='_deviot_port')


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


def createSketch(sketch_name, path):
    from . import Paths
    from .Preferences import Preferences

    # file path
    sketch_path = os.path.join(path, sketch_name)
    if not os.path.exists(sketch_path):
        os.makedirs(sketch_path)

    # use cpp file/template intead of ino
    cpp = Preferences().get('use_cpp', False)
    if cpp:
        ext = '.cpp'
    else:
        ext = '.ino'

    # get template
    template_file_name = 'template' + ext
    preset_path = Paths.getPresetPath()
    template_file_path = os.path.join(preset_path, template_file_name)
    with open(template_file_path) as file:
        src_code = file.read()
    src_file_name = sketch_name + ext
    src_file_path = os.path.join(sketch_path, src_file_name)

    # save new file
    with open(src_file_path, 'w') as src_file:
        src_code = src_code.replace('${src_file_name}', src_file_name)
        src_file.write(src_code)

    # open new file
    views = []
    window = sublime.active_window()
    view = window.open_file(src_file_path)
    views.append(view)
    if views:
        window.focus_view(views[0])


def getDefaultPaths():
    if(sublime.platform() == 'windows'):
        default_path = ["C:\Python27\\", "C:\Python27\Scripts"]
    else:
        default_path = ["/usr/bin", "/usr/local/bin"]
    return default_path


def getHeaders():
    user_agent = 'Deviot/%s (Sublime-Text/%s)' % (__version__,
                                                  sublime.version())
    headers = {'User-Agent': user_agent}
    return headers


def extractTar(tar_path, extract_path='.'):
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
    from .Serial import SerialMonitor
    from . import Serial
    from .Preferences import Preferences

    monitor_module = Serial
    serial_monitor = None

    serial_port = Preferences().get('id_port', '')
    serial_ports = Serial.listSerialPorts()

    # create window and view if not exists
    if window is None:
        window = sublime.active_window()

    if serial_port in serial_ports:
        if serial_port in monitor_module.serials_in_use:
            serial_monitor = monitor_module.serial_monitor_dict.get(
                serial_port, None)
        if not serial_monitor:
            output_view = Preferences().get('deviot_output', False)
            if(not output_view):
                from .Messages import MonitorView
                monitor_view = MonitorView(window, serial_port)
                header = False
            else:
                from .Messages import Console
                monitor_view = Console(window, color=False, monitor=True)
                header = True
            serial_monitor = SerialMonitor(serial_port, monitor_view, header)

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
    from . import Serial
    from .Preferences import Preferences

    monitor_module = Serial

    preferences = Preferences()
    serial_port = preferences.get('id_port', '')
    if serial_port in monitor_module.serials_in_use:
        serial_monitor = monitor_module.serial_monitor_dict.get(
            serial_port, None)
        if serial_monitor and serial_monitor.isRunning():
            serial_monitor.send(text)


def closeSerialMonitors():
    """
    Closes all the serial monitor running

    Arguments:
        preferences {object} -- User preferences instance
    """
    from . import Serial
    from .Preferences import Preferences

    monitor_module = Serial
    in_use = monitor_module.serials_in_use

    if in_use:
        for port in in_use:
            cur_serial_monitor = monitor_module.serial_monitor_dict.get(
                port, None)
            if cur_serial_monitor:
                Preferences().set('autorun_monitor', True)
                cur_serial_monitor.stop()
            monitor_module.serials_in_use.remove(port)


def getKeywords():
    """
    Gets the keywords from the installed libraries

    Returns:
        [list] -- list of object with the keywords
    """
    from . import Paths
    from . import Keywords

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
    from . import Paths
    from .JSONFile import JSONFile

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
    from . import Paths
    from .JSONFile import JSONFile

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
    headers = listHeadersFromSrc(src_text)

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


def listHeadersFromSrc(src_text):
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
    if path.endswith(('.ino', '.pde')):
        window.open_file(path)

    files = os.path.join(path, '*')
    files = glob.glob(files)

    for file in files:
        if file.endswith(('.ino', '.pde')):
            window.open_file(file)


def removePreferences():
    from shutil import rmtree
    from . import Paths

    plug_path = Paths.getPluginPath()
    dst = os.path.join(plug_path, 'Settings-Default', 'Main.sublime-menu')
    user_path = Paths.getDeviotUserPath()
    main_menu = Paths.getSublimeMenuPath()

    # remove files
    rmtree(user_path, ignore_errors=False)
    os.remove(main_menu)
    os.remove(dst)


def getEnvironment():
    from .Preferences import Preferences

    # Get the environment based in the current file
    native = Preferences().get('native', False)

    if native:
        environment = Preferences().get('native_env_selected', False)
    else:
        environment = Preferences().get('env_selected', False)

    return environment


def getInitPath(view):
    workingpath = getWorkingPath(view)
    inipath = os.path.join(workingpath, 'platformio.ini')

    return inipath


def saveEnvironment(data):
    from .Preferences import Preferences

    settings = Preferences()

    # Save data
    native = settings.get('native', True)

    if(native):
        settings.set('native_env_selected', data)
    else:
        settings.set('env_selected', data)


def getEnvFromFile():
    from .configobj.configobj import ConfigObj

    window = sublime.active_window()
    view = window.active_view()

    inipath = getInitPath(view)

    envs = []
    if(os.path.exists(inipath)):
        inifile = ConfigObj(inipath)
        for env in inifile:
            if('env' in env):
                envs.append(env.split(":")[1])
    return envs


def getJSONBoards(force=False):
    from . import Paths
    # check if json file is saved
    data_file = Paths.getTemplateMenuPath('platformio_boards.json',
                                          user_path=True)

    if(not os.path.isfile(data_file) or force):
        from .PlatformioCLI import PlatformioCLI
        PlatformioCLI().getAPIBoards()


def checkEnvironments():
    from .Preferences import Preferences

    settings = Preferences()

    enabled = settings.get('enable_menu', False)
    if(enabled):
        if(settings.get('force_native', False)):
            native = True
        else:
            native = settings.get('native', True)
        if(native):
            env = settings.get('native_env_selected', False)
            enabled = True if env else False
        else:
            env = settings.get('env_selected', False)
            enabled = True if env else False

    return enabled


def isNativeProject(view):
    """
    Checks if the file in the given view has been initialized
    or not and set the project as native if the file structure
    is like PlatformIO or not native if is diferent. If the file
    isn't initialized and 'force_native' is check it will be
    always native.

    Returns:
            [bolean] - True if it's native, false if isn't
    """
    file_path = view.file_name()

    from .Preferences import Preferences
    from . import Paths

    force_native = Preferences().get('force_native', False)

    # only if file has been saved
    if(file_path):
        parent_path = Paths.getParentPath(file_path)
        native = False

        # find platformio.ini
        for file in os.listdir(parent_path):
            if(file.endswith('platformio.ini')):
                Preferences().set('native', True)
                return True

    # check if horce native was selected
    if(force_native):
        native = True

    # if is stored in the temp folder set as native
    if(not force_native):
        if("Temp" in file_path or "tmp" in file_path):
            native = True

    # save in preferences file
    Preferences().set('native', native)

    return native


def checkIniFile(path):
    """
    Check if platformio.ini exist in the given path
    """
    if(os.path.isdir(path)):
        for file in os.listdir(path):
            if(file.endswith('platformio.ini')):
                return True
    return False


def isIniFile(view):
    """
    Check if platformio.ini exist
    """
    from . import Paths

    filepath = getPathFromView(view)
    tempname = getNameFromPath(filepath, ext=False)
    inipath = Paths.getBuildPath(tempname)
    check = checkIniFile(inipath)

    return check


def getWorkingPath(view):
    from . import Paths
    from .Preferences import Preferences

    filepath = Paths.getCWD(view.file_name())
    parentpath = os.path.dirname(filepath)
    init_native = checkIniFile(parentpath)

    if(init_native or filepath.endswith('src')):
        returnpath = parentpath
    else:
        tempname = getNameFromPath(filepath, ext=False)
        returnpath = Paths.getBuildPath(tempname)

        force = Preferences().get('native', True)

        if(force):
            returnpath = filepath

    return returnpath

ERRORS_LIST = []


def highlightError(view, conf=False):
    from re import search

    # Default config
    if(not conf):
        icon = 'Packages/Theme - Default/dot.png'
        flag = sublime.DRAW_NO_FILL
    else:
        icon = conf['icon']
        flag = conf['flag']

    idn = 0
    errors_list = []

    region = sublime.Region(0, view.size())
    sketch = view.substr(region)

    for text in sketch.splitlines():
        if('before' in text):
            string_before = search(u'\'(\w+)\'$', text).group(1)

        if 'error:' in text:
            r_error = []
            before = False
            before_found = False
            previous_line = False
            # error is in previous line
            if('before' in text):
                before = True

            text = text.split('error:')[0].strip()
            infos = text.split(':')

            if ':/' in text:
                file_path = infos[0] + ':' + infos[1]
                infos.pop(0)
                infos.pop(0)
            else:
                file_path = infos[0]
                infos.pop(0)

            line_no = int(infos[0])
            column_no = int(infos[1])

            file_view = view.window().open_file(file_path)
            current_line = ""
            sketch_name = file_view.file_name().replace('\\', '_')

            # get view
            while(not current_line):
                point = file_view.text_point(line_no, column_no)
                line = file_view.line(point)
                current_line = file_view.substr(line)

                point = file_view.text_point(line_no - 1, column_no)
                line = file_view.line(point)
                previous_line = file_view.substr(line)

                if(string_before in current_line):
                    before_found = True

                if(not before_found or not previous_line):
                    current_line = ""

                line_no = line_no - 1

            if(before):
                point = file_view.text_point(line_no, column_no)
                line = file_view.line(point)

            key_name = sketch_name + str(idn)
            errors_list.append(key_name)

            r_error.append(sublime.Region(line.a, line.b))
            file_view.add_regions(key_name, r_error, 'invalid', icon, flag)

            if(not idn):
                file_view.show(point)

            idn = idn + 1

    return errors_list


def highlightRemove(errors_list):
    from time import sleep

    return_list = []
    view = sublime.active_window().active_view()
    file_name = view.file_name().replace('\\', '_')

    for error in errors_list:
        if(file_name in error):
            view.erase_regions(error)
        else:
            return_list.append(error)

    return return_list


def runCommand(command, cwd=None):
    '''Commands

    Run all the commands to install the plugin

    Arguments:
        command {[list]} -- [list of commands]

    Keyword Arguments:
        cwd {[str]} -- [current working dir] (default: {None})

    Returns:
        [list] -- list[0]: return code list[1]: command output
    '''
    import subprocess

    command.append("2>&1")
    command = ' '.join(command)
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, cwd=cwd,
                               universal_newlines=True, shell=True)

    output = process.communicate()
    stdout = output[0]
    return_code = process.returncode

    if(return_code > 0):
        print(stdout)

    return (return_code, stdout)
