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
import urllib.parse
import urllib.request
from codecs import decode

from . import __version__ as version
from . import Paths
from .JSONFile import JSONFile
from .Preferences import Preferences
from .Menu import Menu
from . import Tools
from .Progress import ThreadProgress
from .Commands import CommandsPy
from . import Messages
from .Messages import MessageQueue
from multiprocessing.pool import ThreadPool


class Libraries():
    """
    Handle the library API from platformIO
    More info: http://docs.platformio.org/en/latest/librarymanager/index.html
    """

    def __init__(self, window=None, view=None):
        self.view = view
        self.window = None
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
        # show result in the quick panel
        self.window.run_command('show_results')
        return
        # building query
        request = {}
        request['query'] = keyword
        query = urllib.parse.urlencode(request)

        # request parameters
        url = 'http://api.platformio.org/lib/search?'
        user_agent = 'Deviot/' + str(version) + \
            ' (Sublime-Text/' + str(sublime.version()) + ')'
        headers = {'User-Agent': user_agent}
        req = urllib.request.Request(url + query, headers=headers)

        # receive first page
        with urllib.request.urlopen(req) as response:
            list = json.loads(response.read().decode(encoding='UTF-8'))

        # check number of pages
        nloop = list['total'] / list['perpage']
        if(nloop > 1):
            # next pages
            nloop = int(nloop) + 1 if nloop > int(nloop) else nloop
            for page in range(2, nloop + 1):
                # building query of next pages
                request['page'] = page
                query = urllib.parse.urlencode(request)
                req = urllib.request.Request(url + query, headers=headers)
                # receive first page
                with urllib.request.urlopen(req) as response:
                    page_next = json.loads(
                        response.read().decode(encoding='UTF-8'))
                    for item_next in page_next['items']:
                        list['items'].append(item_next)

        # save data in file
        self.saveLibrary(list, 'default_list.json')
        # show result in the quick panel
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

        # arrange list to the quickpanel
        quick_list = []
        for item in list['items']:
            if(str(item['id']) + ' ' not in ",".join(list_ins)):
                item_list = []
                item_list.append(item['name'])
                item_list.append(item['description'])
                item_list.append(str(item['id']))
                quick_list.append(item_list)

        self.saveLibrary(quick_list, 'quick_list.json')
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
        self.message_queue.put('[ Deviot ]\\n')

        # Install Library with CLI
        command = ['lib', 'install %s' % lib_id]
        self.Commands.runCommand(command, extra_message=lib_name)

        # Save id in preferences
        if (not self.Commands.error_running):
            installed = self.Preferences.get('user_libraries', '')
            if(installed):
                if(lib_id not in installed):
                    self.Preferences.data.setdefault(
                        'user_libraries', []).append(lib_id)
                    self.Preferences.saveData()
            else:
                self.Preferences.set('user_libraries', [lib_id])

    def writeLibrary(self, name):
        self.toggleLibrary(name)

    def removeList(self):
        Tools.setStatus(self.view, 'Preparing List', True)
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self.removeListCli)
        output = async_result.get()
        Tools.setStatus(self.view, 'List Ready', True, 2000)

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
            quick_list = ['None Library Installed']

        self.saveLibrary(quick_list, 'quick_list.json')
        return quick_list

    def removeListCli(self):
        command = ['lib', 'list --json-output']
        Commands = CommandsPy()
        output = Commands.runCommand(command, setReturn=True)
        output = json.loads(output)
        return output

    def removeLibrary(self, selected):
        list = self.getLibrary('quick_list.json')
        lib_id = list[selected][2]
        lib_name = list[selected][0]

        # uninstall Library with CLI
        command = ['lib', 'uninstall %s' % lib_id]
        self.Commands.runCommand(command, extra_message=lib_name)

        # remove from preferences
        if (not self.Commands.error_running):
            installed = self.Preferences.get('user_libraries', '')
            if(installed):
                if(lib_id in installed):
                    self.Preferences.data.setdefault(
                        'user_libraries', []).remove(lib_id)
                    self.Preferences.saveData()

    def toggleLibrary(self, name):
        installed = self.Preferences.get('user_libraries', False)

        if(installed):
            if name in installed:
                self.Preferences.data.setdefault(
                    'user_libraries', []).remove(name)
            else:
                self.Preferences.data.setdefault(
                    'user_libraries', []).append(name)
            self.Preferences.saveData()
        else:
            self.Preferences.set('user_libraries', [name])
        self.getInstalledList()

    def getInstalledList(self):
        # get file and preferences
        order_list = self.getLibrary('order_list.json')
        list = self.Preferences.get('user_libraries', '')

        installed_list = []
        for name, items in order_list.items():
            if(name in list):
                item_list = []
                item_list.append(name)
                item_list.append(items['description'])
                installed_list.append(item_list)

        return installed_list

    def saveLibrary(self, data, file_name):
        libraries_path = Paths.getLibraryPath()
        library_path = os.path.join(libraries_path, file_name)
        libraries = JSONFile(library_path)
        libraries.setData(data)
        libraries.saveData()

    def getLibrary(self, file_name):
        plugin_path = Paths.getLibraryPath()
        library_path = os.path.join(plugin_path, file_name)
        libraries = JSONFile(library_path).getData()

        return libraries


def openInThread(type, window, keyword):
    if(type == 'download'):
        thread = threading.Thread(
            target=Libraries(window).downloadList, args=(keyword,))
        thread.start()
        ThreadProgress(thread, 'Searching', 'Done')
    elif(type == 'install'):
        thread = threading.Thread(
            target=Libraries(window).installLibrary, args=(keyword,))
        thread.start()
        ThreadProgress(thread, 'Installing', 'Done')
    elif(type == 'remove'):
        thread = threading.Thread(
            target=Libraries(window).removeLibrary, args=(keyword,))
        thread.start()
        ThreadProgress(thread, 'Removing', 'Done')
