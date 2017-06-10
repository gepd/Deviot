# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sublime

from ..beginning import __version__


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


def getHeaders():
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
    env_path = get_setting('env_path', False)

    if(not env_path):
        return command

    from . import paths
    bin_dir = paths.getEnvBinDir()

    _os = sublime.platform()

    if(_os is 'osx'):
        exe = 'python'
        options = ['-m', command[0]]
    else:
        exe = command[0]
        options = []

    executable = os.path.join(bin_dir, exe)
    cmd = ['"%s"' % (executable)]
    cmd.extend(options)
    cmd.extend(command[1:])

    return cmd


def run_command(command, cwd=None):
    '''
    Run a command with Popen and return the results or print the errors
    '''
    import subprocess

    command = create_command(command)
    command.append("2>&1")
    command = ' '.join(command)
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, cwd=cwd,
                               universal_newlines=True, shell=True)

    output = process.communicate()
    stdout = output[0]
    return_code = process.returncode

    return (return_code, stdout)

def get_setting(key, default=None):
    """
    get setting handled by ST
    """
    from sublime import load_settings

    settings = load_settings("Deviot/deviot.sublime-settings")

    return settings.get(key, default)


def save_setting(key, value):
    """
    save setting handled by ST
    """
    from sublime import load_settings, save_settings

    settings = load_settings("Deviot/deviot.sublime-settings")
    settings.set(key, value)
    save_settings("Deviot/deviot.sublime-settings")


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


def create_sketch(path, sketch_name):
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
