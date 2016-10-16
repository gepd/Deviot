# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sys
import sublime

from ..libraries import tools, paths


def get_pio_version():
    """
    Get the current version instaled of PlatformIO
    """
    cmd = ['pio', '--version']
    return tools.run_command(cmd)


def check_pio():
    """
    check if PlatformIO is installed
    """
    from re import match

    out = get_pio_version()
    error_code = out[0]

    if(error_code):
        return 103

    if(not error_code):
        version = match(r"\w+\W \w+ (.+)", out[1]).group(1)

    return 200


def install():
    """
    install PlatformIO
    """

    I_STATE = 200
    os.environ['PATH'] = tools.get_env_paths()

    env_file_path = paths.getEnvFile()
    env_dir_path = paths.getVirtualenvPath()
    denv_dir_path = paths.getDenvPath()
    bin_dir_path = paths.getEnvBinDir()

    # download virtualenv file
    I_STATE = save_virtualenv_file(env_file_path)
    if(I_STATE != 200):
        return I_STATE

    # extract and rename folder
    I_STATE = prepare_virtualenv(env_dir_path, env_file_path, denv_dir_path)
    if(I_STATE != 200):
        return I_STATE

    # install virtualenv
    I_STATE = install_virtual_env(denv_dir_path, env_dir_path)
    if(I_STATE != 200):
        return I_STATE

    # remove virtualenv folder
    from shutil import rmtree
    rmtree(env_dir_path)

    # save environments
    env_path = [denv_dir_path, bin_dir_path]
    tools.save_env_paths(env_path)

    # Install PlatFormIO
    I_STATE = install_pio()
    update_version_file()

    return I_STATE


def check_upgrade():
    """
    check if PlatformIO is up to date
    """
    from re import sub

    out = get_pio_version()
    error_code = out[0]
    version = sub(r'\D', '', out[1])

    try:
        from urllib.request import Request
        from urllib.request import urlopen
        import json

        url = 'https://pypi.python.org/pypi/platformio/json'
        req = Request(url, headers=tools.getHeaders())
        response = urlopen(req)
        list = json.loads(response.read().decode())
    except:
        return 102

    published_version = sub(r'\D', '', list['info']['version'])

    if(version != published_version):
        return 104
    return 200


def upgrade():
    # try to update
    out = tools.run_command(['pip', 'install', '-U', 'platformio'])
    print(out[1])
    # error updating
    if(out[0] > 0):
        return 110
    return 200


def update_version_file():
    """
    update the version saved in the config file
    """
    from re import sub

    out = get_pio_version()
    version = sub(r'\D', '', out[1])

    tools.saveConfig('version', version)

    return 200


def get_pio_install_state():
    installed = tools.getConfig('pio_installed', False)
    if(not installed):
        return 103
    return 200


def set_pio_installed():
    """
    Set PlatformIO as installed in the config file
    """
    tools.saveConfig('pio_installed', True)


def save_virtualenv_file(env_file_path):
    # check if virtualenv file is cached
    cached_file = False
    if(os.path.exists(env_file_path)):
        cached_file = True

    if(not cached_file):
        url_file = 'https://pypi.python.org/packages/source/v/' \
            'virtualenv/virtualenv-14.0.6.tar.gz'

        try:
            from urllib.request import Request
            from urllib.request import urlopen

            file_request = Request(url_file, headers=tools.getHeaders())
            file_open = urlopen(file_request)
            file = file_open.read()
        except:
            return 105

        # save file
        try:
            output = open(env_file_path, 'wb')
            output.write(bytearray(file))
            output.close()
        except:
            return 106
    return 200


def prepare_virtualenv(env_dir_path, env_file_path, denv_dir_path):

    try:
        # extract file
        if(not os.path.isdir(env_dir_path)):
            tools.extractTar(env_file_path, denv_dir_path)

        # rename folder
        extracted = os.path.join(denv_dir_path, 'virtualenv-14.0.6')
        if(not os.path.isdir(env_dir_path)):
            os.rename(extracted, env_dir_path)
    except:
        return 107
    return 200


def install_virtual_env(denv_dir_path, env_dir_path):
    settings = sublime.load_settings("Deviot.sublime-settings")
    pylink = settings.get('pylink', 'python')

    cmd = [pylink, 'virtualenv.py', '"%s"' % denv_dir_path]
    out = tools.run_command(cmd, env_dir_path)

    if(out[0] > 0):
        return 108
    return 200


def install_pio():
    cmd = ['pip', 'install', '-U', 'platformio']
    out = tools.run_command(cmd)

    if(out[0] > 0):
        return 109
    return 200
