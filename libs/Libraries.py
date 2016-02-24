#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import json
import time
import sublime
import threading

try:

    from . import Paths
    from . import Tools
    from . import Messages
    from . import __version__ as version
    from .JSONFile import JSONFile
    from .Preferences import Preferences
    from .Progress import ThreadProgress
    from .Commands import CommandsPy
    from .Messages import MessageQueue
    from .I18n import I18n
except:
    import libs.Paths as Paths
    import libs.Tools as Tools
    from libs import Messages
    from libs import __version__ as version
    from libs.JSONFile import JSONFile
    from libs.Preferences import Preferences
    from libs.Progress import ThreadProgress
    from libs.Commands import CommandsPy
    from libs.Messages import MessageQueue
    from libs.I18n import I18n

if(Tools.getPythonVersion() < 3):
    from urllib import urlencode
    from urllib2 import Request
    from urllib2 import urlopen
else:
    from urllib.parse import urlencode
    from urllib.request import Request
    from urllib.request import urlopen

_ = I18n().translate


class Libraries:
    """
    Handle the library API from platformIO
    More info: http://docs.platformio.org/en/latest/librarymanager/index.html
    """

    def __init__(self, window=None, view=None):
        self.view = view
        self.window = window
        self.Preferences = Preferences()

        # create window and view if not exists
        if self.window is None:
            self.window = sublime.active_window()
        self.view = self.window.active_view()

        # console
        console_name = 'Deviot|Library' + str(time.time())
        console = Messages.Console(self.window, name=console_name)

        # Queue for the user console
        self.message_queue = MessageQueue(console)

        # CLI
        self.Commands = CommandsPy(console=console)

    def downloadList(self, keyword):
        """
        Search a library in the platformio API api.platformio.org
        the data of all pages are stored in a json file. The result
        of the search is showing in the st quick panel

        Arguments:
            keyword {string}:
                Keyword to search the library in the platformio API
        """
        # building query
        request = {}
        request['query'] = keyword
        query = urlencode(request)

        # request parameters
        url = 'http://api.platformio.org/lib/search?'
        user_agent = 'Deviot/' + str(version) + \
            ' (Sublime-Text/' + str(sublime.version()) + ')'
        headers = {'User-Agent': user_agent}
        req = Request(url + query, headers=headers)

        # receive first page
        response = urlopen(req)
        list = json.loads(response.read().decode())

        # check number of pages
        nloop = list['total'] / list['perpage']
        if(nloop > 1):
            # next pages
            nloop = int(nloop) + 1 if nloop > int(nloop) else nloop
            for page in range(2, nloop + 1):
                # building query of next pages
                request['page'] = page
                query = urlencode(request)
                req = Request(url + query, headers=headers)
                # receive first page
                response = urlopen(req)
                page_next = json.loads(response.read().decode())
                for item_next in page_next['items']:
                    list['items'].append(item_next)

        # save data in file
        self.saveLibraryData(list, 'default_list.json')
        # show result in the quick panel
        sublime.set_timeout(self.show_results, 0)

    def show_results(self):
        self.window.run_command('show_results')

    def getList(self):
        """
        Gets the list with all libraries found and returns
        on the quick panel

        Returns:
            [dict] -- dictionary with all libraries found
        """
        # get file
        list = self.getLibrary('default_list.json')
        list_ins = self.Preferences.get('user_libraries', '')

        # if none result
        if(list['total'] == 0):
            list = [_('none_lib_found')]
            return list

        # arrange list to the quickpanel
        quick_list = []
        for item in list['items']:
            if(str(item['id']) + ' ' not in " ".join(list_ins) + ' '):
                item_list = []
                item_list.append(item['name'])
                item_list.append(item['description'])
                item_list.append(str(item['id']))
                quick_list.append(item_list)

        # save and return data
        self.saveLibraryData(quick_list, 'quick_list.json')
        return quick_list

    def installLibrary(self, selected):
        """
        Install the selected library

        Arguments:
            selected {int}
                position in dict of the library selected
        """
        list = self.getLibrary('quick_list.json')
        lib_id = list[selected][2]
        lib_name = list[selected][0]

        self.message_queue.startPrint()
        self.message_queue.put('[ Deviot {0} ]\\n', version)
        time.sleep(0.01)

        # Install Library with CLI
        command = ['lib', 'install', lib_id]
        self.Commands.runCommand(command, extra_message=lib_name)

        # update list of libraries installed in the preference file
        self.getInstalledList(ids=True)
        # update menu
        Tools.updateMenuLibs()

    def installedList(self):
        """
        Show the installed libraries.

        Returns:
            [dict] -- dictionary with the data to show in the quick panel
        """
        list = self.getLibrary('quick_list.json')
        return list

    def getInstalledList(self, ids=False):
        """
        Run the CLI command to get the list of library(ies) installed,
        stores the data in a json file and run a command to show the
        quick panel with all the data founded
        """
        command = ['lib', 'list', '--json-output']
        Commands = CommandsPy()
        output = Commands.runCommand(command, setReturn=True)
        output = json.loads(output)

        # return a dict with the ids of the installed libraries
        if(ids):
            installed_ids = []
            if(output):
                for item in output:
                    installed_ids.append(str(item['id']))
                self.Preferences.set('user_libraries', installed_ids)
                return

        # arrange list to the quickpanel
        quick_list = []
        if(output):
            for item in output:
                item_list = []
                item_list.append(item['name'])
                item_list.append(item['description'])
                item_list.append(str(item['id']))
                quick_list.append(item_list)
        else:
            quick_list = [_('none_lib_installed')]

        # save the data and run the quick panel
        self.saveLibraryData(quick_list, 'quick_list.json')
        self.window.run_command('show_remove_list')

    def removeLibrary(self, selected):
        """
        Run a CLI command with the ID of the library to uninstall,
        also remove the reference of the ID in the preferences file.

        Arguments:
            selected {int}
                position of the option selected in the quick panel.
        """
        list = self.getLibrary('quick_list.json')
        lib_id = list[selected][2]
        lib_name = list[selected][0]

        self.message_queue.startPrint()
        self.message_queue.put('[ Deviot {0} ]\\n', version)
        time.sleep(0.01)

        # uninstall Library with CLI
        command = ['lib', 'uninstall', lib_id]
        self.Commands.runCommand(command, extra_message=lib_name)

        # remove from preferences
        if (not self.Commands.error_running):
            installed = self.Preferences.get('user_libraries', '')
            if(installed):
                if(lib_id in installed):
                    self.Preferences.data.setdefault(
                        'user_libraries', []).remove(lib_id)
                    self.Preferences.saveData()

        # update menu
        Tools.updateMenuLibs()

    def saveLibraryData(self, data, file_name):
        """
        Stores the data of the libraries in a json file

        Arguments:
            data {json}
                json data with the libraries
            file_name {string}
                name of the json file
        """
        libraries_path = Paths.getLibraryPath()
        library_path = os.path.join(libraries_path, file_name)
        libraries = JSONFile(library_path)
        libraries.setData(data)
        libraries.saveData()

    def getLibrary(self, file_name):
        """
        Get a specific json file and return the data

        Arguments:
            file_name {string}
                Json file name where is stored the library data

        Returns:
            [dict] -- Dictionary with the library data
        """
        plugin_path = Paths.getLibraryPath()
        library_path = os.path.join(plugin_path, file_name)
        libraries = JSONFile(library_path).getData()

        return libraries


def openInThread(type, window=None, keyword=None):
    """
    Open differents methods in a new thread (Download, Install,
    Remove library) and show a progress message in the status bar.

    Arguments:
        type {string} -- string with the name of thread to run

    Keyword Arguments:
        window {object} -- Object with the current windows of ST {Default:None}
        keyword {string} -- String with board selected {Default: None}
    """
    if(type == 'download'):
        thread = threading.Thread(
            target=Libraries(window).downloadList, args=(keyword,))
        thread.start()
        ThreadProgress(thread, _('searching'), _('done'))
    elif(type == 'install'):
        thread = threading.Thread(
            target=Libraries(window).installLibrary, args=(keyword,))
        thread.start()
        ThreadProgress(thread, _('installing'), _('done'))
    elif(type == 'list'):
        thread = threading.Thread(target=Libraries().getInstalledList)
        thread.start()
        ThreadProgress(thread, _('preparing_list'), _('done'))
    elif(type == 'remove'):
        thread = threading.Thread(
            target=Libraries(window).removeLibrary, args=(keyword,))
        thread.start()
        ThreadProgress(thread, _('removing'), _('done'))
