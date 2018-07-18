#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import sublime
import sublime_plugin

from os import path, rename
from threading import Thread
from urllib.request import Request
from urllib.request import urlopen
from urllib.error import HTTPError

from ..api import deviot
from ..libraries.thread_progress import ThreadProgress
from ..libraries.file import File

dprint = None
logger = logging.getLogger('Deviot')


class InstallPIO(object):

    def __init__(self, window=False):

        thread = Thread(target=self.install)
        thread.start()
        ThreadProgress(thread, 'processing', '')

    def install(self):
        '''Install Pio in virtualenv

        Check if Pio is in the system if it don't, downloads the virtualenv
        script and install platformIO on it. The state of the installation
        is displayed on the console
        '''
        logger.debug("Starting Setup")
        show_messages()

        dprint("downloading_files")
        self.download_file()

        dprint("extracting_files")
        self.extract_file()

        # install virtualenv
        dprint("installing_pio")

        symlink = deviot.get_sysetting('symlink', 'python')

        cmd = [symlink, 'virtualenv.py', '"%s"' % deviot.dependencies_path()]

        logger.debug("cmd: %s", cmd)

        out = deviot.run_command(cmd, cwd=deviot.virtualenv_path())

        logger.debug("output: %s", out)

        cmd = deviot.prepare_command(['pip', 'install', '-U', 'platformio'])

        logger.debug("cmd: %s", cmd)

        out = deviot.run_command(cmd, cwd=deviot.bin_path())

        logger.debug("output: %s", out)

        if(out[0] == 0):
            deviot.save_sysetting('installed', True)
            deviot.save_sysetting('deviot_bin', True)

            save_env_paths()
            save_board_list()

            dprint("setup_finished")
            logger.debug("Setup done")
        else:
            dprint("setup_error")
            logger.debug("PIO not installed")

    def download_file(self):
        """Download File

        Download the virtualenv file
        """
        logger.debug("download file")

        if(not cached_file()):
            try:
                logger.debug("downloading: %s", deviot.VIRTUALENV_URL)

                file_request = Request(deviot.VIRTUALENV_URL,
                                       headers=deviot.header())
                file_open = urlopen(file_request)
                file = file_open.read()
            except HTTPError as e:
                logger.error("failed to download", exc_info=True)
                dprint("error_downloading_files")

            try:
                deviot.create_dirs(deviot.cache_path())
                output = open(deviot.virtualenv_file(), 'wb')
                output.write(bytearray(file))
                output.close()

                logger.debug("file stored in: %s", deviot.virtualenv_file())
            except (OSError, FileNotFoundError) as e:
                logger.error("error saving file", exc_info=True)
                dprint("error_saving_files")

    def extract_file(self):
        """Extract File

        Extract the file and rename the output folder
        """
        logger.debug("extracting file")

        virtualenv_dir = deviot.virtualenv_path()

        if(not path.isdir(virtualenv_dir)):
            extract_tar(deviot.virtualenv_file(), deviot.dependencies_path())

            logger.debug("done")

        # rename folder
        extr = path.join(deviot.dependencies_path(), "virtualenv-16.0.0")
        if(not path.isdir(virtualenv_dir)):
            logger.debug("rename folder from %s to %s", extr, virtualenv_dir)

            rename(extr, virtualenv_dir)

            logger.debug("done")


def cached_file():
    """Cached File

    Check if the virtualenvfile was already downloaded
    """
    is_cached = bool(path.isfile(deviot.virtualenv_file()))
    logger.debug("check cache: %s", is_cached)
    return is_cached


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


def save_env_paths():
    """Environment
    After install all the necessary dependencies to run the plugin,
    the environment paths are stored in the preferences file
    Arguments:
        new_path {[list]} -- list with extra paths to store
    """
    env_paths = deviot.environment_paths()
    deviot.save_sysetting('env_paths', env_paths)


def save_board_list():
    paths = deviot.get_sysetting('env_paths', False)
    cmd = deviot.pio_command(['boards', '--json-output'])
    boards = deviot.run_command(cmd, env_paths=paths)[1]

    deviot.create_dirs(deviot.user_pio_path())

    board_file_path = deviot.boards_file_path()
    File(board_file_path).write(boards)


def already_installed():
    show_messages()
    dprint("pio_is_installed")


def show_messages():
    """Show message in deviot console

    Using the MessageQueue package, this function
    start the message printer queue. (call it from the begining)

    global variables

    dprint overrides `message.put()` instead calling it that way,
    dprint() will make the same behavior
    """
    from ..libraries.messages import Messages

    global dprint

    message = Messages()
    message.initial_text("deviot_setup{0}", deviot.version())
    message.create_panel()
    dprint = message.print
