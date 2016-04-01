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
import platform
from shutil import rmtree, copy
from re import match

try:
    from urllib.request import Request
    from urllib.request import urlopen
    from collections import OrderedDict

    from . import Paths
    from . import Tools
    from . import Messages
    from . import __version__ as version
    from .Preferences import Preferences
    from .I18n import I18n
except:
    from urllib2 import Request
    from urllib2 import urlopen
    from libs.OrderedDict import OrderedDict

    import libs.Paths as Paths
    import libs.Tools as Tools
    from libs import Messages
    from libs import __version__ as version
    from libs.Preferences import Preferences
    from libs.I18n import I18n

_ = I18n().translate

class PioInstall(object):

    def __init__(self):
        self.Preferences = Preferences()
        self.base_dir = Paths.getDeviotUserPath()
        self.env_dir = Paths.getEnvDir()
        self.env_bin_dir = Paths.getEnvBinDir()
        self.cache_dir = Paths.getCacheDir()
        self.env_file = Paths.getEnvFile()
        self.cached_file = False
        self.os = Tools.getOsName()

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
                _("deviot_need_python"), _("button_download_python"))
            if(go_to):
                sublime.run_command(
                    'open_url', {'url': 'https://www.python.org/downloads/'})
            return

        # check if pio is installed
        self.message_queue.startPrint()
        self.message_queue.put("deviot_setup{0}", version)
        current_time = time.strftime('%H:%M:%S')

        # get pio version
        if(self.os == 'osx'):
            executable = os.path.join(self.env_bin_dir, 'python')
            cmd = ['"%s"' % (executable), '-m', 'platformio', '--version']
        else:
            executable = os.path.join(self.env_bin_dir, 'pio')
            cmd = ['"%s"' % (executable), '--version']
        out = childProcess(cmd)

        if(out[0] == 0):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put("pio_is_installed{0}", current_time)

            self.endSetup()
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
        Tools.extractTar(self.env_file, tmp)

        # install virtualenv in a temp dir
        current_time = time.strftime('%H:%M:%S')
        self.message_queue.put("installing_pio{0}", current_time)

        temp_env = os.path.join(tmp, 'env-root')
        cwd = os.path.join(tmp, 'virtualenv-14.0.1')
        cmd = ['python', 'setup.py', 'install', '--root', temp_env]
        out = childProcess(cmd, cwd)

        # error
        if(out[0] > 0):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put("error_installing_env_{0}", current_time)
            return

        # make vitualenv
        for root, dirs, files in os.walk(tmp):
            for file in files:
                if(file == 'virtualenv.py'):
                    cwd = root

        if(os.path.exists(cwd)):
            cmd = ['python', 'virtualenv.py', '"%s"' % (self.env_dir)]
            out = childProcess(cmd, cwd)

            # error
            if(out[0] > 0):
                current_time = time.strftime('%H:%M:%S')
                self.message_queue.put("error_making_env_{0}", current_time)
                return

        # remove temp dir
        rmtree(tmp)

        # install pio
        if(self.os == 'osx'):
            executable = os.path.join(self.env_bin_dir, 'python')
            cmd = ['"%s"' % (executable), '-m', 'pip', 'install', '-U', 'platformio']
        else:
            executable = os.path.join(self.env_bin_dir, 'pip')
            cmd = ['"%s"' % (executable), 'install', '-U', 'platformio']
        out = childProcess(cmd)

        # error
        if(out[0] > 0):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put("error_installing_pio_{0}", current_time)
            return

        self.endSetup()

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

    def endSetup(self):
        # save env paths
        if(self.os != 'osx'):
            env_path = [self.env_bin_dir]
            self.saveEnvPaths(env_path)

        # get pio version
        if(self.os == 'osx'):
            executable = os.path.join(self.env_bin_dir, 'python')
            cmd = ['"%s"' % (executable), '-m', 'platformio', '--version']
        else:
            executable = os.path.join(self.env_bin_dir, 'pio')
            cmd = ['"%s"' % (executable), '--version']
        out = childProcess(cmd)

        pio_version = match(r"\w+\W \w+ (.+)", out[1]).group(1)
        self.Preferences.set('pio_version', pio_version)

        # copy menu
        sys_os = Tools.getOsName()
        preset_path = Paths.getPresetPath()
        plg_path = Paths.getPluginPath()
        dst = os.path.join(plg_path, 'Settings-Default', 'Main.sublime-menu')

        if(sys_os == 'windows'):
            if(platform.release() == '7'):
                src_path = os.path.join(preset_path, 'Main.sublime-menu.w7')
            else:    
                src_path = os.path.join(preset_path, 'Main.sublime-menu.windows')
            copy(src_path, dst)
        elif(sys_os == 'osx'):
            src_path = os.path.join(preset_path, 'Main.sublime-menu.osx')
            copy(src_path, dst)
        else:
            src_path = os.path.join(preset_path, 'Main.sublime-menu.linux')
            copy(src_path, dst)

        # creating files (menu, completions, syntax)
        sublime.set_timeout(self.generateFilesCall, 0)

        self.Preferences.set('protected', True)
        self.Preferences.set('enable_menu', True)

    def generateFilesCall(self):
        try:
            from .PlatformioCLI import generateFiles
        except:
            from libs.PlatformioCLI import generateFiles

        generateFiles(install=True)

    def checkUpdate(self):
        self.message_queue.startPrint()
        self.message_queue.put('_deviot_{0}', version)
        self.message_queue.put('checking_pio_updates')
        
        # try to update
        if(self.os == 'osx'):
            executable = os.path.join(self.env_bin_dir, 'python')
            cmd = ['"%s"' % (executable), '-m', 'pip', 'install', '-U', 'platformio']
        else:
            executable = os.path.join(self.env_bin_dir, 'pip')
            cmd = ['"%s"' % (executable), 'install', '-U', 'platformio']
        out = childProcess(cmd)

        # error updating
        if(out[0] > 0):
            self.message_queue.put('error_pio_updates')
            return

        # get version
        if(self.os == 'osx'):
            executable = os.path.join(self.env_bin_dir, 'python')
            cmd = ['"%s"' % (executable), '-m', 'platformio', '--version']
        else:
            executable = os.path.join(self.env_bin_dir, 'pio')
            cmd = ['"%s"' % (executable), '--version']
        out = childProcess(cmd)

        pio_old_ver = self.Preferences.get('pio_version', 0)
        pio_new_ver = match(r"\w+\W \w+ (.+)", out[1]).group(1)

        # pio up to date
        if(pio_new_ver == pio_old_ver):
            self.message_queue.put('pio_up_date{0}', pio_new_ver)
            self.Preferences.set('pio_version', pio_new_ver)
            return
        # pio update installed
        elif(pio_new_ver > pio_old_ver):
            self.message_queue.put('pio_new_updated_installed{0}', pio_new_ver)
            self.Preferences.set('pio_version', pio_new_ver)
            return


def childProcess(command, cwd=None):
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
