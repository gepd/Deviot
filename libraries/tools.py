# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from re import search
from shutil import rmtree
from os import environ, path, makedirs, getenv, remove
from sublime import load_settings, save_settings, platform, version, active_window, windows, Region, LAYOUT_BELOW
from ..libraries import __version__

H_EXTS = ['.h']
ROOT_PATH = 'System Root(/)'
INCLUDE = r'^\s*#include\s*[<"](\S+)[">]'
PHANTOMS = []
VPHANTOMS = {}

def accepted_extensions():
    """
    Files accepted to be processed by deviot
    """
    accepted = ['ino', 'pde', 'cpp', 'c', 'S', 'h']
    return accepted

def get_env_paths():
    '''
    All the necessary environment paths are merged to run platformIO
    '''

    from collections import OrderedDict

    # default paths
    if(platform() == 'windows'):
        default_paths = ["C:\Python27\\", "C:\Python27\Scripts"]
    else:
        default_paths = ["/usr/bin", "/usr/local/bin"]

    system_paths = environ.get("PATH", "").split(path.pathsep)

    env_paths = []
    env_paths.extend(default_paths)
    env_paths.extend(system_paths)

    env_paths = list(OrderedDict.fromkeys(env_paths))
    env_paths = path.pathsep.join(env_paths)

    return env_paths


def save_env_paths(new_path):
    '''
    After install all the necessary dependencies to run the plugin,
    the environment paths are stored in the preferences file
    '''
    from collections import OrderedDict

    env_paths = get_env_paths().split(path.pathsep)

    paths = []
    paths.extend(new_path)
    paths.extend(env_paths)

    paths = list(OrderedDict.fromkeys(paths))
    paths = path.pathsep.join(paths)

    save_setting('env_path', paths)


def get_headers():
    """
    headers for urllib request
    """

    user_agent = 'Deviot/%s (Sublime-Text/%s)' % (__version__, version())
    headers = {'User-Agent': user_agent}
    return headers

def create_command(command):
    """
    Edit the command depending of the O.S of the user
    """
    external_bins = get_sysetting('external_bins', False)
    env_path = get_sysetting('env_path', False)
    symlink = get_sysetting('symlink', False)

    if(not env_path or bool(external_bins)):
        return command

    from .paths import getEnvBinDir

    if(platform() == 'osx'):
        exe = 'python' if(not bool(symlink)) else 'python2'
        options = ['-m', command[0]]
    else:
        exe = command[0]
        options = []

    bin_dir = getEnvBinDir()
    executable = path.join(bin_dir, exe)

    cmd = ['"%s"' % (executable)]
    cmd.extend(options)
    cmd.extend(command[1:])

    return cmd

def get_sysetting(key, default=None):
    """
    Stores the setting in the file:
    Packages/User/Deviot/deviot.ini
    """
    from ..libraries.readconfig import ReadConfig
    from .paths import getSystemIniPath
 
    section = "config"
    sys_path = getSystemIniPath()

    config = ReadConfig()
    
    # remove config file if it's currupted
    if(config.bad_format()):
        from .path import packages_path
        ini = path.join(packages_path, 'User', 'Deviot', 'deviot.ini')
        
        if(path.exists(ini)):
            remove(ini)


    config.read(sys_path)

    if(not config.has_option(section, key)):
        return default
    
    return config.get(section, key)[0]

def save_sysetting(key, value):
    """
    Gets the setting stored in the file 
    Packages/User/Deviot/deviot.ini
    """
    from ..libraries.readconfig import ReadConfig
    from .paths import getSystemIniPath

    section = "config"
    sys_path = getSystemIniPath()

    config = ReadConfig()
    config.read(sys_path)

    if(not config.has_section(section)):
        config.add_section(section)

    config.set(section, key, value)

    with open(sys_path, 'w') as configfile:
        config.write(configfile)

def get_setting(key, default=None):
    """
    get setting handled by ST
    """
    settings = load_settings("deviot.sublime-settings")
    return settings.get(key, default)


def save_setting(key, value=None, sys_options=False):
    """
    save setting handled by ST
    """
    settings = load_settings("deviot.sublime-settings")

    if(value == None):
        settings.erase(key)
    else:
        settings.set(key, value)

    save_settings("deviot.sublime-settings")

def remove_settings():
    """
    Removes the deviot.sublime-settings and
    Packages/User/Deviot folder
    """
    from .paths import getPluginPath, getPackagesPath, getDenvPath 
    
    plugin_path = getPluginPath()
    packages_path = getPackagesPath()
    deviot_penv = getDenvPath()

    deviot_menu = path.join(plugin_path, 'Main.sublime-menu')
    deviot_context = path.join(plugin_path, 'Context.sublime-menu')
    deviot_commands = path.join(plugin_path, 'Default.sublime-commands')
    deviot_settings = path.join(packages_path, 'User', 'deviot.sublime-settings')

    files = [deviot_menu, deviot_context, deviot_commands, deviot_settings]
    folders = [deviot_penv]

    for file in files:
        if(path.exists(file)):
            remove(file)

    for folder in folders:
        if(path.exists(folder)):
            rmtree(folder, ignore_errors=True)

    from .I18n import I18n
    from sublime import message_dialog
    
    _ = I18n().translate

    text = _('restart_sublime')

    message_dialog(text)

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

def make_folder(path):
    """
    Make a folder with the given path
    """
    import errno
    try:
        makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass

def create_sketch(sketch_name, select_path):
    """
    create a new sketch with the name and path given
    the template include a basic code stored in the preset
    folder inside of the plugin
    """
    from . import paths

    ext = None
    sketch = sketch_name.split('.')
    if(len(sketch) > 1):
        ext = '.' + sketch[-1]
        sketch_name = sketch_name.replace(ext, '')

    # file path
    sketch_path = path.join(select_path, sketch_name)
    if not path.exists(sketch_path):
        makedirs(sketch_path)

    if(not ext):
        # use cpp file/template intead of ino
        cpp = get_setting('cpp_file', False)
        if cpp:
            ext = '.cpp'
        else:
            ext = '.ino'

    # get template
    template_file_name = 'template' + ext
    preset_path = paths.getPresetPath()
    template_file_path = path.join(preset_path, template_file_name)
    with open(template_file_path) as file:
        src_code = file.read()
    src_file_name = sketch_name + ext
    src_file_path = path.join(sketch_path, src_file_name)

    # save new file
    with open(src_file_path, 'w') as src_file:
        src_code = src_code.replace('${src_file_name}', src_file_name)
        src_file.write(src_code)

    # open new file
    views = []
    window = active_window()
    view = window.open_file(src_file_path)
    views.append(view)
    if views:
        window.focus_view(views[0])


def findInOpendView(view_name):
    """
    Search a specific view in the list of available views

    Arguments:
        view_name {string}
            Name of the view to search
    """
    opened_view = None
    found = False
    fwindows = windows()
    for window in fwindows:
        views = window.views()
        for view in views:
            name = view.name()
            if name == view_name:
                opened_view = view
                found = True
                break
        if found:
            break
    return (window, opened_view)

def list_win_volume():
    """List Windows Disc
    
    Lists the volumes (disc) availables in Windows
    
    Returns:
        list -- list of directories
    """
    vol_list = []
    for label in range(67, 90):
        vol = chr(label) + ':\\'
        if path.isdir(vol):
            vol_list.append(vol)
    return vol_list


def list_root_path():
    """List of paths
    
    Lists the volumes (disc) availables according
    to the operative sistem
    
    Returns:
        list -- list of directories
    """
    root_list = []
    os_name = platform()
    if os_name == 'windows':
        root_list = list_win_volume()
    else:
        home_path = os.getenv('HOME')
        root_list = [home_path, ROOT_PATH]
    return root_list

def add_library_to_sketch(view, edit, lib_path):
    """Include Library

    Includes a library at the top of the sketch. For example if the
    path given is of the EEPROM library it will add: #include <EEPROM.h>

    To do that, it looks all files with extension '.h' (defined in the 
    H_EXTS var) and compares with the includes already inserted in the
    sketch

    Arguments:
        view {object} -- ST view
        edit {object} -- ST object
        lib_path {string} -- path where library is located
    """
    from glob import glob

    lib_src = path.join(lib_path, 'src')
    
    if path.isdir(lib_src):
        lib_path = lib_src
    
    lib_path = path.join(lib_path, '*')

    region = Region(0, view.size())
    src_text = view.substr(region)
    headers = headers_from_source(src_text)

    h_files = []
    sub_files = glob(lib_path)
    for file in sub_files:
        file_name = path.basename(file)
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


def headers_from_source(src_text):
    """Includes in Source
    
    Gets the library includes already inserted in the sketch

    Arguments:
        src_text {string} -- text string with all the sketch

    Returns:
        [list] -- libraries "include" already existing
    """
    import re

    pattern = re.compile(INCLUDE, re.M | re.S)
    headers = pattern.findall(src_text)
    return headers
