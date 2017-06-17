# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sublime

from sublime import load_settings, save_settings
from ..beginning import __version__

H_EXTS = ['.h']
ROOT_PATH = 'System Root(/)'
INCLUDE = r'^\s*#include\s*[<"](\S+)[">]'

def get_env_paths():
    '''
    All the necessary environment paths are merged to run platformIO
    '''

    from collections import OrderedDict

    # default paths
    if(sublime.platform() == 'windows'):
        default_paths = ["C:\Python27\\", "C:\Python27\Scripts"]
    else:
        default_paths = ["/usr/bin", "/usr/local/bin"]

    system_paths = os.environ.get("PATH", "").split(os.path.pathsep)

    env_paths = []
    env_paths.extend(default_paths)
    env_paths.extend(system_paths)

    env_paths = list(OrderedDict.fromkeys(env_paths))
    env_paths = os.path.pathsep.join(env_paths)

    return env_paths


def save_env_paths(new_path):
    '''
    After install all the necessary dependencies to run the plugin,
    the environment paths are stored in the preferences file
    '''
    from collections import OrderedDict

    env_paths = get_env_paths().split(os.path.pathsep)

    paths = []
    paths.extend(new_path)
    paths.extend(env_paths)

    paths = list(OrderedDict.fromkeys(paths))
    paths = os.path.pathsep.join(paths)

    save_setting('env_path', paths)


def get_headers():
    """
    headers for urllib request
    """

    user_agent = 'Deviot/%s (Sublime-Text/%s)' % (__version__,
                                                  sublime.version())
    headers = {'User-Agent': user_agent}
    return headers


def extractTar(tar_path, extract_path='.'):
    """
    Extrack tar files in a custom path
    """

    import tarfile
    tar = tarfile.open(tar_path, 'r:gz')
    for item in tar:
        tar.extract(item, extract_path)


def create_command(command):
    """
    Edit the command depending of the O.S of the user
    """
    external_bins = get_setting('external_bins', False)
    env_path = get_setting('env_path', False)
    symkink = get_setting('symlink', False)

    if(not env_path):
        return command

    _os = sublime.platform()

    if(_os is 'osx'):
        exe = 'python' if(not symlink) else 'python2'
        options = ['-m', command[0]]
    else:
        exe = command[0]
        options = []

    executable = exe

    if(not external_bins):
        from . import paths
        
        bin_dir = paths.getEnvBinDir()
        executable = os.path.join(bin_dir, exe)

    cmd = ['"%s"' % (executable)]
    cmd.extend(options)
    cmd.extend(command[1:])

    return cmd

def get_setting(key, default=None):
    """
    get setting handled by ST
    """
    settings = load_settings("deviot.sublime-settings")
    return settings.get(key, default)


def save_setting(key, value):
    """
    save setting handled by ST
    """
    settings = load_settings("deviot.sublime-settings")
    settings.set(key, value)
    save_settings("deviot.sublime-settings")

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
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise exc
        pass


def output_in_file(command, file_path):
    """
    run a command who return and output in a json format
    and store it in a file
    """
    from .file import File
    from ..platformio.run_command import run_command

    out = run_command(command)
    boards = out[1]

    # save in file
    file_board = File(file_path)
    file_board.write(boards)

    return 200


def create_sketch(sketch_name, path):
    """
    create a new sketch with the name and path given
    the template include a basic code stored in the preset
    folder inside of the plugin
    """
    from . import paths
    # file path
    sketch_path = os.path.join(path, sketch_name)
    if not os.path.exists(sketch_path):
        os.makedirs(sketch_path)

    # use cpp file/template intead of ino
    cpp = get_setting('use_cpp', False)
    if cpp:
        ext = '.cpp'
    else:
        ext = '.ino'

    # get template
    template_file_name = 'template' + ext
    preset_path = paths.getPresetPath()
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


def findInOpendView(view_name):
    """
    Search a specific view in the list of available views

    Arguments:
        view_name {string}
            Name of the view to search
    """
    opened_view = None
    found = False
    windows = sublime.windows()
    for window in windows:
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
        if os.path.isdir(vol):
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
    os_name = sublime.platform()
    if os_name == 'windows':
        root_list = list_win_volume()
    else:
        home_path = os.getenv('HOME')
        root_list = [home_path, ROOT_PATH]
    return root_list

def select_dir(window, index=-2, level=0, paths=None, key=None, func=None):
    """Select a directory
    
    Show a quick panel with the list of directories (disc, folders) avaialbles to make and action.
    you can select a directory and save a file. This function will return the selected directory and
    will call the 'fuc' argument as callback. The callback will be called like fuc(key, path)
    
    Arguments:
        window {obj} -- sublime text window object
    
    Keyword Arguments:
        index {number} -- Quick panel selection index (default: {-2})
        level {number} -- Directory index level (default: {0})
        paths {str} -- Current path (default: {None})
        key {str} -- key to send in the callback (default: {None})
        func {obj} -- function that works as callback (default: {None})
    """
    from .I18n import I18n

    if index == -1:
        return ''

    if level > 0 and index == 0:
        sel_path = paths[0].split('(')[1][:-1]
        if func:
            if key:
                save_path = [sel_path, index, level]
                if(key == 'default_path'):
                    sel_path = save_path
                save_setting('last_path', save_path)
                func(key, sel_path)
        return

    else:
        if index == 1:
            level -= 1
        elif index > 1:
            level += 1

        default_path = get_setting('default_path', False)
        if(not default_path):
            default_path = get_setting('last_path', False)

        if(index == -2 and default_path):
            paths = [default_path[0]]
            index = default_path[1]
            level = default_path[2]

        if level <= 0:
            level = 0
            dir_path = '.'
            parent_path = '..'

            paths = list_root_path()

        else:
            sel_path = paths[index]
            if sel_path == ROOT_PATH:
                sel_path = '/'
            dir_path = os.path.abspath(sel_path)
            parent_path = os.path.join(dir_path, '..')
            
            from .dir import Dir
            
            cur_dir = Dir(dir_path)
            sub_dirs = cur_dir.list_dirs()
            paths = [d.get_path() for d in sub_dirs]

        _ = I18n().translate

        paths.insert(0, parent_path)
        paths.insert(0, _('select_cur_dir_{0}', dir_path))

    sublime.set_timeout(lambda: window.show_quick_panel(
        paths, lambda index: select_dir(
            window, index, level, paths, key, func)), 5)


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

    lib_src = os.path.join(lib_path, 'src')
    
    if os.path.isdir(lib_src):
        lib_path = lib_src
    
    lib_path = os.path.join(lib_path, '*')

    region = sublime.Region(0, view.size())
    src_text = view.substr(region)
    headers = headers_from_source(src_text)

    h_files = []
    sub_files = glob(lib_path)
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