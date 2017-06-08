#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" INSTALLER

Install platformIO in the user folder of sublime text, it will be done
in the path: Packages/user/penv, this installer will previously check if
platformio is installed in the machine (and accesible) if not, it will
proceed with the installation. 

This code is intended to work as a standalone, so you can call to the
"PioInstall" class and it will run in a new thread and will install all 
the necessary files to run platformio.

Version: 1.0.0
Author: gepd@outlook.com
Licence: Same as the project (Read the LICENCE file in the root)

"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import json
import datetime
import threading
import tempfile
import sublime
import inspect
import sys
from time import strftime
from shutil import rmtree
from re import match, sub
from urllib.request import Request
from urllib.request import urlopen
from collections import OrderedDict

from . import __version__, __title__

from ..libraries.messages import dprint, derror

# TODO
# Add symlink to a config file


class PioInstall(object):

    def __init__(self, window=False):
        self.filePaths()

        thread = threading.Thread(target=self.install)
        thread.start()

    def filePaths(self):
        """ Set Initial Values

        Set the values for files and paths to install platformIO
        """
        self.FILE_URL = 'https://pypi.python.org/packages/source/v/' \
            'virtualenv/virtualenv-14.0.6.tar.gz'

        # Local
        CACHE_FOL = '.cache'  # cache folder name
        VENVA_FOL = 'virtualenv'  # virtualenv folder
        SOURC_FOL = 'penv'  # where virtualenv and pio will be installed

        CURRENT_FILE = os.path.abspath(inspect.getfile(inspect.currentframe()))
        PLUGIN_PATH = os.path.dirname(os.path.dirname(CURRENT_FILE))
        PACKAGE_PATH = os.path.dirname(PLUGIN_PATH)
        DEVIOT_UPATH = os.path.join(PACKAGE_PATH, 'User', 'Deviot')
        CACHE_PATH = os.path.join(DEVIOT_UPATH, CACHE_FOL)
        URL_LIST = self.FILE_URL.split("/")
        URL_COUNT = len(URL_LIST)
        USER_AGENT = 'Deviot/%s (Sublime-Text/%s)' % (__version__,
                                                      sublime.version())

        # global
        self.V_ENV_FILE = os.path.join(CACHE_PATH, URL_LIST[URL_COUNT - 1])
        self.V_ENV_PATH = os.path.join(DEVIOT_UPATH, SOURC_FOL)
        self.V_ENV_BIN_PATH = os.path.join(
            self.V_ENV_PATH, 'Scripts' if 'windows' in sublime.platform() else 'bin')
        self.OUTPUT_PATH = os.path.join(self.V_ENV_PATH, VENVA_FOL)
        self.HEADERS = {'User-Agent': USER_AGENT}
        self.CACHED_FILE = False
        self.SYMLINK = 'python'

        createPath(CACHE_PATH)

        # defining default env paths
        os.environ['PATH'] = getEnvPaths()

    def cachedFile(self):
        """Cached File

        Check if the virtualenvfile was already downloaded
        """
        if(os.path.isfile(self.V_ENV_FILE)):
            self.CACHED_FILE = True
        return self.CACHED_FILE

    def install(self):
        '''Install Pio in virtualenv

        Check if Pio is in the system if it don't, downloads the virtualenv
        script and install platformIO on it. The state of the installation
        is displayed on the console
        '''

        self.checkPython()

        checkPio()

        dprint("Downloading virtualenv")

        self.downloadFile()

        dprint("Extracting file")

        self.extractFile()

        # install virtualenv
        dprint("Installing platformIO")

        cmd = [self.SYMLINK, 'virtualenv.py', '"%s"' % self.V_ENV_PATH]
        out = runCommand(cmd, "error installing virtualenv", self.OUTPUT_PATH)

        # Install pio
        if(sublime.platform() is 'osx'):
            executable = os.path.join(self.V_ENV_BIN_PATH, 'python')
            cmd = ['"%s"' % (executable), '-m', 'pip',
                   'install', '-U', 'platformio']
        else:
            executable = os.path.join(self.V_ENV_BIN_PATH, 'pip')
            cmd = ['"%s"' % (executable), 'install', '-U', 'platformio']
        out = runCommand(cmd, "error installing platformio")

        # save env paths
        env_path = [self.V_ENV_PATH, self.V_ENV_BIN_PATH]
        self.saveEnvPaths(env_path)

        dprint("setup finished")

    def downloadFile(self):
        """Download File

        Download the virtualenv file
        """
        if(not self.cachedFile()):
            try:
                file_request = Request(self.FILE_URL, headers=self.HEADERS)
                file_open = urlopen(file_request)
                file = file_open.read()
            except:
                derror("There was an error downloading virtualenv")

            # save file
            try:
                output = open(self.V_ENV_FILE, 'wb')
                output.write(bytearray(file))
                output.close()
            except:
                derror("There was an error saving virtualenv")

    def extractFile(self):
        """Extract File

        Extract the file and rename the output folder
        """

        if(not os.path.isdir(self.OUTPUT_PATH)):
            extractTar(self.V_ENV_FILE, self.V_ENV_PATH)

        # rename folder
        extracted = os.path.join(self.V_ENV_PATH, 'virtualenv-14.0.6')
        if(not os.path.isdir(self.OUTPUT_PATH)):
            os.rename(extracted, self.OUTPUT_PATH)

    def saveEnvPaths(self, new_path):
        '''Environment

        After install all the necessary dependencies to run the plugin,
        the environment paths are stored in the preferences file

        Arguments:
            new_path {[list]} -- list with extra paths to store
        '''
        env_paths = getEnvPaths().split(os.path.pathsep)

        paths = []
        paths.extend(new_path)
        paths.extend(env_paths)

        paths = list(OrderedDict.fromkeys(paths))
        paths = os.path.pathsep.join(paths)

        # TODO CHECK PREFERENCES
        # self.Preferences.set('env_path', paths)

    def checkSymlink(self):
        """Arch Linux

        Check if python 2 is used with a symkink it's 
        commonly used in python2. When it's used it's
        stored in a config file to be used by the plugin
        """
        cmd = ['python2', '--version']
        out = runCommand(cmd)

        dprint("Symlink detetected")

        if(out[0] is 0):
            self.SYMLINK = 'python2'
            return out

    def checkPython(self):
        """Python requirement

        Check if python 2 is installed
        """
        cmd = [self.SYMLINK, '--version']
        out = runCommand(cmd)

        if(out[0] > 0):
            out = self.checkSymlink()

        version = sub(r'\D', '', out[1])

        # show error and link to download
        if(out[0] > 0 or int(version[0]) is 3):
            go_to = sublime.ok_cancel_dialog(
                "You Need to install python 2", "Download")

            if(go_to):
                sublime.run_command(
                    'open_url', {'url': 'https://www.python.org/downloads/'})
            from sys import exit
            exit(0)


def checkPio():
    """PlarformIO

    Check if platformIO is already installed in the machine
    """
    cmd = ['pio', '--version']
    out = runCommand(cmd)

    status = out[0]

    if(status is 0):
        derror("PlatformIO is already installed")


def createPath(path):
    """
    Create a specifict path if it doesn't exists
    """
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno is not errno.EEXIST:
            raise exc
        pass


def extractTar(tar_path, extract_path='.'):
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


def getEnvPaths():
    '''Environment

    All the necessary environment paths are merged to run platformIO
    correctly

    Returns:
        [list] -- paths in a list
    '''
    # default paths
    default_paths = getDefaultPaths()
    system_paths = os.environ.get("PATH", "").split(os.path.pathsep)

    env_paths = []
    env_paths.extend(default_paths)
    env_paths.extend(system_paths)

    env_paths = list(OrderedDict.fromkeys(env_paths))
    env_paths = os.path.pathsep.join(env_paths)

    return env_paths


def getDefaultPaths():
    """Python Paths

    Folder where python should be installed in the diferents os

    Returns:
        list -- paths corresponding to the os
    """
    if(sublime.platform() is 'windows'):
        default_path = ["C:\Python27\\", "C:\Python27\Scripts"]
    else:
        default_path = ["/usr/bin", "/usr/local/bin"]
    return default_path


def runCommand(command, error='', cwd=None):
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
        derror(error)

    return (return_code, stdout)
