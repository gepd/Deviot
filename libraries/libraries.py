#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime
from json import loads
from threading import Thread
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

from . import __version__ as version
from .tools import get_headers, get_setting, save_setting
from .progress_bar import ProgressBar
from .messages import MessageQueue
from .quick_panel import quick_panel
from .I18n import I18n
from ..platformio.command import Command
from .file import File
from .paths import getLibrariesFileDataPath


class Libraries(Command):
    """
    Handle the library API from platformIO
    More info: http://docs.platformio.org/en/latest/librarymanager/index.html
    """

    def __init__(self, window=None, view=None, feedback=True):
        super(Libraries, self).__init__()

        self.window = sublime.active_window()
        self.view = self.window.active_view()
        self.lib_file_path = getLibrariesFileDataPath()
        self.tr = I18n().translate
        self.quick_list = []
        self.cwd = None

        self.dprint = None
        self.dstop = None

    def set_queue(self):
        """Message Instances
        
        Makes all the instances to start to print in the deviot console.
        It sends a header string as first message
        """
        message = MessageQueue("[ Deviot ] Library Management\n")
        message.start_print()
        
        self.dprint = message.put
        self.dstop = message.stop_print

    def search_library(self):
        """Search Library
        
        Opens the input box to search a library
        """
        caption = self.tr("search_query")
        self.window.show_input_panel(caption, '', self.download_list_async, None, None)

    def download_list_async(self, keyword):
        """Downlad in a Thread
        
        Opens the download_list method in a new thread to avoid blocking
        the main thread of sublime text
        
        Arguments:
            keyword {str} -- keyword to be search
        """
        thread = Thread(target=self.download_list, args=(keyword,))
        thread.start()

    def download_list(self, keyword):
        """PlatformIO API
        
        Search a library in the platformio API api.platformio.org.
        The results are formated in the quick panel way and displayed
        on it

        Arguments:
            keyword {string}:
                Keyword to search the library in the platformio API
        """
        request = {}
        request['query'] = keyword
        query = urlencode(request)

        url = 'http://api.platformio.org/lib/search?{0}*'.format(query)
        req = Request(url, headers=get_headers())

        response = urlopen(req)
        response_list = loads(response.read().decode())

        nloop = response_list['total'] / response_list['perpage']
        if(nloop > 1):

            nloop = int(nloop) + 1 if nloop > int(nloop) else int(nloop)
            for page in range(2, nloop + 1):

                request['page'] = page
                query = urlencode(request)
                req = Request(url + query, headers=get_headers())

                response = urlopen(req)
                page_next = loads(response.read().decode())
                for item_next in page_next['items']:
                    response_list['items'].append(item_next)

        if(len(response_list['items']) == 0):
            self.quick_list.append([self.tr('none_lib_found')])
        else:
            self.quicked(response_list['items'])
            self.quick_list.insert(0, [self.tr('select_library').upper()])
        
        quick_panel(self.quick_list, self.library_install_async)

    def quicked(self, source_list):
        """Quick panel List
        
        Turn the source dictionary list in a only list
        format to work properly in the quick panel
        
        Arguments:
            source_list {dict} -- dictionary with data
        """
        quick_list = []
        
        for item in source_list:
            id = item['id']
            name = item['name']
            description = item['description']
            frameworks = ''
            
            for framework in item['frameworks']:
                frameworks += framework + ' '
            
            info = "{0} | {1}".format(id, frameworks)
            quick_list.append([name, description, info])

        self.quick_list = quick_list


    def library_install_async(self, selected):
        """Install in thread
        
        Runs the library_install method to avoid block the main
        thread of sublime text
        
        Arguments:
            selected {int} -- user selection index
        """
        if(selected <= 0):
            return

        thread = Thread(target=self.library_install, args=(selected,))
        thread.start()

    def library_install(self, selected):
        """Library Install
        
        Run a CLI command with the ID of the library to install. After the 
        setup finished it adds the library information in the boards.json 
        file.

        Arguments:
            selected {int} -- user selection index
        """
        lib_id = self.quick_list[selected][2].split(' ')[0]
        lib_name = self.quick_list[selected][0]

        self.set_queue()

        cmd = ['lib', '--global', 'install', lib_id]
        out = self.run_command(cmd)

        if(out[0] == 0):
            quick_list = File(self.lib_file_path).read_json()
            quick_list.append(self.quick_list[selected])

            File(self.lib_file_path).save_json(quick_list)


    def get_installed_list(self):
        """Install libraries list
        
        Get the file with the installed libraries. This files
        is updated each time the user install or remove a library,
        the file is formated in the quick panel way (list)
        """
        quick_list = File(self.lib_file_path).read_json()

        self.quick_list = quick_list
        self.quick_list.insert(0, [self.tr('select_library').upper()])

        quick_panel(quick_list, self.remove_library_async)

    def remove_library_async(self, selected):
        """Remove in a thread
        
        Runs the remove_library method to avoid block the main
        thread of sublime text
        
        Arguments:
            selected {int} -- user selection index
        """
        if(selected <= 0):
            return

        thread = Thread(target=self.remove_library, args=(selected,))
        thread.start()

    def remove_library(self, selected):
        """Remove Library
    
        Run a CLI command with the ID of the library to uninstall,
        it also removes the reference from the libraries.json file.

        Arguments:
            selected {int} -- user selection index.
        """
        response_list = self.quick_list

        lib_id = self.quick_list[selected][2].split(' ')[0]
        lib_name = self.quick_list[selected][0]

        self.set_queue()

        cmd = ['lib', '--global', 'uninstall', lib_id]
        out = self.run_command(cmd)

        if(out[0] == 0):
            self.quick_list.remove(self.quick_list[selected])
            
            File(self.lib_file_path).save_json(self.quick_list)

    def save_installed_list(self):
        """Save installed list
        
        Each time a library is installed or removed, it's stored/delted
        in a file (libraries.json). This file is used to avoid the lag
        when you run the platformIO command. If for some reason the list
        of libraries are corrupted or out of date, this method will updated
        the file to get the most recent information
        """
        self.set_return = True
        self.realtime = False

        cmd = ['lib', '--global', 'list', '--json-output']
        out = self.run_command(cmd)
        out = loads(out)

        self.quicked(out)

        File(self.lib_file_path).save_json(self.quick_list)