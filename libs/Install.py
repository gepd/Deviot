#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import time
import tempfile
import sublime
import subprocess
from shutil import rmtree

try:
    from urllib.request import Request
    from urllib.request import urlopen
    from collections import OrderedDict

    from . import Paths
    from . import Tools
    from . import Messages
    from . import __version__ as version
    from .Preferences import Preferences
    from .PlatformioCLI import generateFiles
except:
    from urllib2 import Request
    from urllib2 import urlopen
    from libs.OrderedDict import OrderedDict

    import libs.Paths as Paths
    import libs.Tools as Tools
    from libs import Messages
    from .libs.Preferences import Preferences


class PioInstall(object):

    def __init__(self):
        self.Preferences = Preferences()
        self.base_dir = Paths.getDeviotUserPath()
        self.env_dir = Paths.getEnvDir()
        self.env_bin_dir = Paths.getEnvBinDir()
        self.cache_dir = Paths.getCacheDir()
        self.env_file = Paths.getEnvFile()
        self.cached_file = False

        # console
        window = sublime.active_window()
        console_name = 'Deviot|Pio_Install' + str(time.time())
        console = Messages.Console(window, name=console_name)

        # Queue for the user console
        self.message_queue = Messages.MessageQueue(console)

    def checkPio(self):
        # defining default env paths
        os.environ['PATH'] = self.getEnvPaths()

        # checking python
        cmd = ['python', '--version']
        out = childProcess(cmd)

        # show error and link to download
        if(out[0] > 0):
            current_time = time.strftime('%H:%M:%S')
            go_to = sublime.ok_cancel_dialog(
                "deviot_need_python", "button_download_python")
            if(go_to):
                sublime.run_command(
                    'open_url', {'url': 'https://www.python.org/downloads/'})
            return

        # check if pio is installed
        self.message_queue.startPrint()
        self.message_queue.put("deviot_setup{0}", version)
        current_time = time.strftime('%H:%M:%S')

        cmd = ['pio', '--version']
        out = childProcess(cmd)

        if(out[0] == 0):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put("pio_is_installed{0}", current_time)
            return

        current_time = time.strftime('%H:%M:%S')
        self.message_queue.put("pio_isn_installed{0}", current_time)

        # check if virtualenv file is cached
        if(os.path.exists(self.env_file)):
            self.cached_file = True

        # download virtualenv
        if(not self.cached_file):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put("downloading_files{0}", current_time)
            headers = Tools.getHeaders()
            url_file = 'https://pypi.python.org/packages/source/v/virtualenv/virtualenv-14.0.1.tar.gz'

            try:
                file_request = Request(url_file, headers=headers)
                file_open = urlopen(file_request)
                file = file_open.read()
            except:
                current_time = time.strftime('%H:%M:%S')
                self.message_queue.put(
                    "error_downloading_files{0}", current_time)
                print("There was an error downloading virtualenv")
                return
            # save file
            try:
                output = open(self.env_file, 'wb')
                output.write(bytearray(file))
                output.close()
            except:
                current_time = time.strftime('%H:%M:%S')
                self.message_queue.put("error_saving_files{0}", current_time)
                print("There was an error saving the virtualenv file")
                return

        # extract file
        current_time = time.strftime('%H:%M:%S')
        self.message_queue.put("extracting_files{0}", current_time)
        tmp = tempfile.mkdtemp()
        Tools.extract_tar(self.env_file, tmp)

        # install virtualenv in a temp dir
        current_time = time.strftime('%H:%M:%S')
        self.message_queue.put("{0} Installing Platformio...\n", current_time)

        temp_env = os.path.join(tmp, 'env-root')
        cwd = os.path.join(tmp, 'virtualenv-14.0.1')
        cmd = ['python', 'setup.py', 'install', '--root', temp_env]
        childProcess(cmd, cwd)

        # make vitualenv
        cwd = os.path.join(tmp, 'env-root', 'Python27', 'Lib', 'site-packages')
        if(os.path.exists(cwd)):
            cmd = ['python', 'virtualenv.py', '\"' + self.env_dir + '\"']
            childProcess(cmd, cwd)

        # remove temp dir
        rmtree(tmp)

        # install pio
        executable = os.path.join(self.env_bin_dir, 'pip')
        cmd = ['\"' + executable + '\"', 'install', 'platformio']
        childProcess(cmd)

        # get pio version
        cmd = ['pio', '--version']
        out = childProcess(cmd)

        pio_version = match(r"\w+\W \w+ (.+)", out[1]).group(1)
        self.Preferences.set('pio_version', pio_version)

        # save env paths
        env_path = [self.env_bin_dir]
        self.saveEnvPaths(env_path)

        # creating files (menu, completions, syntax)
        generateFiles()

        current_time = time.strftime('%H:%M:%S')
        self.message_queue.put("setup_finished{0}", current_time)

    def getEnvPaths(self):
        # default paths
        default_paths = Tools.getDefaultPaths()
        system_paths = os.environ.get("PATH", "").split(os.path.pathsep)

        env_paths = []
        env_paths.extend(default_paths)
        env_paths.extend(system_paths)

        env_paths = list(OrderedDict.fromkeys(env_paths))
        env_paths = os.path.pathsep.join(env_paths)

        return env_paths

    def saveEnvPaths(self, new_path):
        env_paths = self.getEnvPaths().split(os.path.pathsep)

        paths = []
        paths.extend(new_path)
        paths.extend(env_paths)

        paths = list(OrderedDict.fromkeys(paths))
        paths = os.path.pathsep.join(paths)

        self.Preferences.set('env_path', paths)
        self.Preferences.set('protected', True)
        self.Preferences.set('enable_menu', True)


def childProcess(command, cwd=None):
    command.append("2>&1")
    command = ' '.join(command)
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, cwd=cwd,
                               universal_newlines=True, shell=True)

    output = process.communicate()
    stdout = output[0]
    stderr = output[1]
    return_code = process.returncode

    return (return_code, stdout)
