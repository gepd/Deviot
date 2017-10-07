#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" INSTALLER

Install platformIO in the user folder of sublime text, it will be done
in the path: Packages/user/penv, this installer will previously check if
platformio is installed in the machine (and accesible) if not, it will
proceed with the installation. 

This code is intended to work as a standalone, so you can call to the
"PioInstall" class and it will run in a new thread and will install all 
the necessary files to run platformio. (replace or remove dprint, derror,
show_message() and show_error()) all inside ### are external libraries

Version: 1.0.0
Author: Guillermo Díaz
Contact: gepd@outlook.com
Licence: Same as the project (Read the LICENCE file in the root)

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime

from os import path, environ, makedirs, rename
from inspect import getfile, currentframe
from threading import Thread
from sys import exit
from time import strftime
from shutil import rmtree
from re import match, sub
from urllib.request import Request
from urllib.request import urlopen
from collections import OrderedDict
from ..libraries import __version__, __title__

###
from ..libraries.syntax import Syntax
from ..libraries.tools import get_setting, save_setting
from ..libraries.tools import get_sysetting, save_sysetting
from ..libraries.paths import getSystemIniPath, getPackagesPath
from ..libraries.thread_progress import ThreadProgress
from ..libraries.I18n import I18n
from ..platformio.pio_bridge import PioBridge

dprint = None
derror = None
dstop = None
###


class PioInstall(object):

    def __init__(self, window=False):
        self.dev_ver = __version__
        self.sub_ver = sublime.version()

        beginning_check()

        ###
        installed = get_sysetting('installed', False)
        if(not installed):
            found = self.check_old_settings()
            if(found):
                return

        if(bool(installed)):
            return

        Syntax()

        show_messages()
        dprint("deviot_setup{0}", True, self.dev_ver)
        ###

        self.file_paths()

        caption = I18n().translate('processing')
        thread = Thread(target=self.install)
        thread.start()
        ThreadProgress(thread, caption, '')

    def check_old_settings(self):
        """
        All the dynamic settings are being stored in the 
        deviot.ini file instead of the deviot.sublime-settings.
        To avoid make the user remove all the preferences and
        run the setup process again, this function will move the
        preferences automatically
        """
        found = False
        settings = ['env_path', 'symlink', 'external_bins', 'last_check_update',
                    'last_action', 'installed']

        for setting in settings:
            current = get_setting(setting)
            if(current):
                save_sysetting(setting, current)
                save_setting(setting)
                found = True

        return found

    def file_paths(self):
        """ Set Initial Values

        Set the values for files and paths to install platformIO
        """
        self.FILE_URL = 'https://pypi.python.org/packages/source/v/' \
            'virtualenv/virtualenv-14.0.6.tar.gz'

        # Local
        CACHE_FOL = '.cache'  # cache folder name
        VENVA_FOL = 'virtualenv'  # virtualenv folder
        SOURC_FOL = 'penv'  # where virtualenv and pio will be installed

        CURRENT_FILE = path.abspath(getfile(currentframe()))
        PLUGIN_PATH = path.dirname(path.dirname(CURRENT_FILE))
        PACKAGE_PATH = path.dirname(PLUGIN_PATH)
        DEVIOT_UPATH = path.join(PACKAGE_PATH, 'User', 'Deviot')
        CACHE_PATH = path.join(DEVIOT_UPATH, CACHE_FOL)
        URL_LIST = self.FILE_URL.split("/")
        URL_COUNT = len(URL_LIST)
        USER_AGENT = 'Deviot/%s (Sublime-Text/%s)' % (self.dev_ver,
                                                      self.sub_ver)

        # global
        self.V_ENV_FILE = path.join(CACHE_PATH, URL_LIST[URL_COUNT - 1])
        self.V_ENV_PATH = path.join(DEVIOT_UPATH, SOURC_FOL)
        self.V_ENV_BIN_PATH = path.join(
            self.V_ENV_PATH, 'Scripts' if 'windows' in sublime.platform() else 'bin')
        self.OUTPUT_PATH = path.join(self.V_ENV_PATH, VENVA_FOL)
        self.HEADERS = {'User-Agent': USER_AGENT}
        self.CACHED_FILE = False
        self.SYMLINK = 'python'

        create_path(CACHE_PATH)

        # defining default env paths
        environ['PATH'] = get_env_paths()

    def cached_file(self):
        """Cached File

        Check if the virtualenvfile was already downloaded
        """
        if(path.isfile(self.V_ENV_FILE)):
            self.CACHED_FILE = True
        return self.CACHED_FILE

    def install(self):
        '''Install Pio in virtualenv

        Check if Pio is in the system if it don't, downloads the virtualenv
        script and install platformIO on it. The state of the installation
        is displayed on the console
        '''

        self.check_python()

        check_pio()

        dprint("pio_isn_installed")
        dprint("downloading_files")

        self.download_file()

        dprint("extracting_files")

        self.extract_file()

        # install virtualenv
        dprint("installing_pio")

        cmd = [self.SYMLINK, 'virtualenv.py', '"%s"' % self.V_ENV_PATH]
        out = run_command(cmd, "setup_error", self.OUTPUT_PATH)

        # Install pio
        if(sublime.platform() == 'osx'):
            executable = path.join(self.V_ENV_BIN_PATH, self.SYMLINK)
            cmd = ['"%s"' % (executable), '-m', 'pip',
                   'install', '-U', 'platformio']
        else:
            executable = path.join(self.V_ENV_BIN_PATH, 'pip')
            cmd = ['"%s"' % (executable), 'install', '-U', 'platformio']
        out = run_command(cmd, "setup_error")

        # save env paths
        env_path = [self.V_ENV_PATH, self.V_ENV_BIN_PATH]
        save_env_paths(env_path)

        save_sysetting('installed', True)
        PioBridge().save_boards_list()

        derror("setup_finished")

    def download_file(self):
        """Download File

        Download the virtualenv file
        """
        if(not self.cached_file()):
            try:
                file_request = Request(self.FILE_URL, headers=self.HEADERS)
                file_open = urlopen(file_request)
                file = file_open.read()
            except:
                derror("error_downloading_files")

            # save file
            try:
                output = open(self.V_ENV_FILE, 'wb')
                output.write(bytearray(file))
                output.close()
            except:
                derror("error_saving_files")

    def extract_file(self):
        """Extract File

        Extract the file and rename the output folder
        """

        if(not path.isdir(self.OUTPUT_PATH)):
            extract_tar(self.V_ENV_FILE, self.V_ENV_PATH)

        # rename folder
        extracted = path.join(self.V_ENV_PATH, 'virtualenv-14.0.6')
        if(not path.isdir(self.OUTPUT_PATH)):
            rename(extracted, self.OUTPUT_PATH)

    def check_sym_link(self):
        """Arch Linux

        Check if python 2 is used with a symlink it's
        commonly used in python2. When it's used it's
        stored in a config file to be used by the plugin
        """
        cmd = ['python2', '--version']
        out = run_command(cmd)

        if(out[0] == 0):
            dprint("symlink_detected")
            self.version = sub(r'\D', '', out[1])
            self.SYMLINK = 'python2'
            save_sysetting('symlink', True)

    def check_python(self):
        """Python requirement

        Check if python 2 is installed
        """
        self.version = None

        cmd = [self.SYMLINK, '--version']
        out = run_command(cmd)

        if(out[0] == 0):
            self.version = sub(r'\D', '', out[1])

        if(self.version and int(self.version[0]) is 3):
            self.check_sym_link()

        # show error and link to download
        if(out[0] > 0 or int(self.version[0]) is 3):
            from ..libraries.I18n import I18n
            _ = I18n().translate
            go_to = sublime.ok_cancel_dialog(
                _("deviot_need_python"), _("button_download_python"))

            if(go_to):
                sublime.run_command(
                    'open_url', {'url': 'https://www.python.org/downloads/'})
            
            exit(0)


def beginning_check():
    """Beginning check

    Checks to do at start sublime text.
    Telemetry will be always disabled and could be possible to activate
    in the deviot or o.s terminal. (pio settings set enable_telemetry yes) 
    """
    # disable telemetry
    telemetry_check = get_sysetting('telemetry_check', False)
    if(not telemetry_check):
        cmd = ['platformio', 'settings', 'set', 'enable_telemetry', 'no']
        out = run_command(cmd)

        if(out[0] == 0):
            save_sysetting('telemetry_check', True)


def check_pio():
    """PlarformIO

    Check if platformIO is already installed in the machine
    """
    cmd = ['platformio', '--version']
    out = run_command(cmd)

    status = out[0]

    if(status is 0):
        env_path = get_env_paths()
        save_sysetting('installed', True)
        save_sysetting('external_bins', True)
        save_sysetting('env_path', env_path)
        PioBridge().save_boards_list()
        derror("pio_is_installed")

def create_path(path):
    """
    Create a specifict path if it doesn't exists
    """
    import errno
    try:
        makedirs(path)
    except OSError as exc:
        if exc.errno is not errno.EEXIST:
            raise exc
        pass


def extract_tar(tar_path, extract_path='.'):
    """Extract File

    Extract a tar file in the selected folder

    Arguments:
        tar_path {str} -- tar file path

    Keyword Arguments:
        extract_path {str} -- location to extract it (default: {'.'})
    """
    import tarfile
    tar = tarfile.open(tar_path, 'r:gz')
    for item in tar:
        tar.extract(item, extract_path)


def get_env_paths():
    '''Environment

    All the necessary environment paths are merged to run platformIO
    correctly

    Returns:
        [list] -- paths in a list
    '''
    # default paths
    default_paths = get_default_paths()
    system_paths = environ.get("PATH", "").split(path.pathsep)

    env_paths = []
    env_paths.extend(default_paths)
    env_paths.extend(system_paths)

    env_paths = list(OrderedDict.fromkeys(env_paths))
    env_paths = path.pathsep.join(env_paths)

    return env_paths

def save_env_paths(new_path):
    '''Environment

    After install all the necessary dependencies to run the plugin,
    the environment paths are stored in the preferences file

    Arguments:
        new_path {[list]} -- list with extra paths to store
    '''
    env_paths = get_env_paths().split(path.pathsep)

    paths = []
    paths.extend(new_path)
    paths.extend(env_paths)

    paths = list(OrderedDict.fromkeys(paths))
    paths = path.pathsep.join(paths)

    save_sysetting('env_path', paths)


def get_default_paths():
    """Python Paths

    Folder where python should be installed in the diferents os

    Returns:
        list -- paths corresponding to the os
    """
    if(sublime.platform() == 'windows'):
        default_path = ["C:\Python27\\", "C:\Python27\Scripts"]
    else:
        user_bin_path = path.join(path.expanduser('~'), '.local', 'bin')
        default_path = ["/usr/bin", "/usr/local/bin", user_bin_path]

    # get path from python.txt in Packages/User/Deviot
    packages_path = getPackagesPath()
    deviot_path = path.join(packages_path, 'User', 'Deviot')
    extra_python = path.join(deviot_path, 'python.txt')

    if(path.exists(extra_python)):
        with open(extra_python) as file:
            for line in file:
                line = line.strip()
                new_path = path.normpath(line)
                default_path.append(new_path)

    return default_path


def run_command(command, error='', cwd=None):
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

    if(return_code > 0 and error is not ''):
        dprint(error)
        derror(stdout)

    return (return_code, stdout)

def show_messages():
    """Show message in deviot console
    
    Using the MessageQueue package, this function
    start the message printer queue. (call it from the begining)
    
    global variables

    dprint overrides `message.put()` instead calling it that way, 
    dprint() will make the same behavior

    derror will print the message in the console but will stop the
    execution of the code

    dstop is the reference of the stop_print method in the MessageQueue
    class, it will called when derror is executed
    """
    from ..libraries.messages import MessageQueue

    global dprint
    global derror
    global dstop

    message = MessageQueue()
    message.start_print()
    dprint = message.put
    derror = show_error
    dstop = message.stop_print

def show_error(text, *args):
    """Show Error
    
    When it's called print the error in the console but stop the
    execution of the program after doing it

    Use this function calling derror()
    
    Arguments:
        text {str} -- message to show in the console
        *args {str} -- strings to be replaced with format()
    """
    dprint(text, False, *args)
    dstop()
    exit(0)