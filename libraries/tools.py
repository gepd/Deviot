# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from re import search
from os import environ, path, makedirs, getenv
from sublime import load_settings, save_settings, platform, version, active_window, windows, Region, LAYOUT_BELOW
from ..libraries import __version__

H_EXTS = ['.h']
ROOT_PATH = 'System Root(/)'
INCLUDE = r'^\s*#include\s*[<"](\S+)[">]'
PHANTOMS = []
VPHANTOMS = {}

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
    symlink = get_setting('python_symlink', 'python')

    if(not env_path):
        return command

    _os = platform()

    if(_os is 'osx'):
        options = ['-m', command[0]]
    else:
        options = []

    executable = symlink

    if(not external_bins):
        from . import paths
        
        bin_dir = paths.getEnvBinDir()
        executable = path.join(bin_dir, symlink)

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
    import errno
    try:
        makedirs(path)
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
    sketch_path = path.join(path, sketch_name)
    if not path.exists(sketch_path):
        makedirs(sketch_path)

    # use cpp file/template intead of ino
    cpp = get_setting('cpp_file', False)
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

    lib_src = os.path.join(lib_path, 'src')
    
    if os.path.isdir(lib_src):
        lib_path = lib_src
    
    lib_path = os.path.join(lib_path, '*')

    region = Region(0, view.size())
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

def show_phanthom(view, text):
    """Display phantom
    
    Given a error text, this function extract the file name,
    line and colum error and the error message and display it
    with a phantom.

    The PHANTOM global var stores the name of all phantoms added
    so it can be removed anytime.

    VPHANTOM stores the view corresponding to the phantom added
    
    Arguments:
        view {obj} -- sublime text view object
        text {str} -- error text extracted from PlatformIO
    """
    global PHANTOMS
    global VPHANTOMS

    result = search("(.+)\:(\d+)\:(\d+):\s\S+\: (.+)", text)

    if(not result):
        return
    
    err_file = view.file_name()
    file = path.normpath(result.group(1))
    line = result.group(2)
    column = result.group(3)
    txt = result.group(4)

    if(err_file != file):
        view = active_window().open_file(file)

    stylesheet = '''
            <style>
                div.error {
                    padding: 0.4rem 0.4rem 0.4rem 0.7rem;
                    margin: 0.2rem 0;
                    border-radius: 2px;
                    border: 1px solid white;
                }
                div.error span.message {
                    color: white;
                    padding-right: 0.7rem;
                }

                div.error a {
                    text-decoration: inherit;
                    padding: 0.35rem 0.7rem 0.45rem 0.8rem;
                    position: relative;
                    bottom: 0.05rem;
                    border-radius: 0 2px 2px 0;
                    font-weight: bold;
                }
                html.dark div.error a {
                    background-color: #00000018;
                }
                html.light div.error a {
                    background-color: #ffffff18;
                }
            </style>
        '''

    phantom_name = str('error' + line)
    content = '<body id=deviot-error>' + \
                stylesheet + \
                '<div class="error"><span class="message">' + \
                txt + \
                '</span> <a href=hide>' + \
                chr(0x00D7) + \
                '</a></div><body>'
    
    tp = view.text_point(int(line) - 1, int(column) - 1)
    region = Region(tp, view.line(tp).b)
    
    erase = lambda href: view.erase_phantoms(phantom_name)
    view.add_phantom(phantom_name, region, content, LAYOUT_BELOW, on_navigate=erase)
    
    PHANTOMS.append(phantom_name)
    VPHANTOMS[phantom_name] = view

def get_phantoms():
    """Phantom names
    
    Get the name (id) of all phantoms, stored in the global PHANTOM
    variable, (currently showing)
    
    Returns:
        list -- phantom names (id)
    """
    global PHANTOMS
    
    return PHANTOMS

def del_phantom(phantom_id):
    """Remove phantom
    
    Removes from the PHANTOMS and VPHANTOMS global variables the
    references to the given phantom
    
    Arguments:
        phantom_id {str} -- phantom name
    """
    global PHANTOMS
    global VPHANTOMS
    
    view = VPHANTOMS[phantom_id]
    view.erase_phantoms(phantom_id)
    
    PHANTOMS.remove(phantom_id)
    del VPHANTOMS[phantom_id]

def reset_phantoms():
    """Clean view
    
    Removes all phantoms showing in the current view
    and also cleans PHANTOM and PHANTOMS global variables
    """
    global PHANTOMS
    global VPHANTOMS

    for pname in PHANTOMS:
        del_phantom(pname)