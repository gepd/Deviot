#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sublime import active_window
from os import path
from json import loads
from glob import glob
from threading import Thread
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen

from . import __version__ as version
from .file import File
from .I18n import I18n
from .messages import MessageQueue
from .quick_panel import quick_panel
from ..platformio.command import Command
from .thread_progress import ThreadProgress
from .tools import get_headers, get_setting, save_setting
from .paths import getLibrariesFileDataPath, getPioPackages, getPioLibrary

_ = None

class Libraries(Command):
    """
    Handle the library API from platformIO
    More info: http://docs.platformio.org/en/latest/librarymanager/index.html
    """

    def __init__(self, window=None, view=None, feedback=True):
        super(Libraries, self).__init__()

        global _
        
        _ = I18n().translate
        self.window = active_window()
        self.view = self.window.active_view()
        self.lib_file_path = getLibrariesFileDataPath()
        self.quick_list = []
        self.cwd = None

        self.dprint = None
        self.dstop = None

    def set_queue(self):
        """Message Instances
        
        Makes all the instances to start to print in the deviot console.
        It sends a header string as first message
        """
        message = MessageQueue("deviot_library{0}", version)
        message.start_print()
        
        self.dprint = message.put
        self.dstop = message.stop_print

    def search_library(self):
        """Search Library
        
        Opens the input box to search a library
        """
        caption = _("search_query")
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
        ThreadProgress(thread, _('searching'), '')

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
            self.quick_list.append([_('none_lib_found')])
        else:
            self.quicked(response_list['items'])
            self.quick_list.insert(0, [_('select_library').upper()])
        
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
        ThreadProgress(thread, _('installing'), '')

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

        self.dstop()

        if(out[0] == 0):
            quick_list = File(self.lib_file_path).read_json()
            quick_list.append(self.quick_list[selected])

            File(self.lib_file_path).save_json(quick_list)
            from .syntax import Syntax
            Syntax()

    def update_library_async(self, selected):
        """Update
        
        Show the installed libraries to search updates
        """
        if(selected <= 0):
            return

        thread = Thread(target=self.update_library, args=(selected,))
        thread.start()
        ThreadProgress(thread, _('updating'), '')

    def update_library(self, selected):
        """Update Library
    
        Run a CLI command with the ID of the library to update

        Arguments:
            selected {int} -- user selection index.
        """
        response_list = self.quick_list

        lib_id = self.quick_list[selected][2].split(' ')[0]
        lib_name = self.quick_list[selected][0]

        self.set_queue()

        cmd = ['lib', '--global', 'update', lib_id]
        out = self.run_command(cmd)

        self.dstop()

    def get_installed_list(self, type):
        """Install libraries list
        
        Get the file with the installed libraries. This files
        is updated each time the user install or remove a library,
        the file is formated in the quick panel way (list)
        
        Arguments:
            type {str} -- action to do after show the quick list
        """
        quick_list = File(self.lib_file_path).read_json()

        self.quick_list = quick_list
        self.quick_list.insert(0, [_('select_library').upper()])

        if(type == 'remove'):
            quick_panel(quick_list, self.remove_library_async)
        else:
            quick_panel(quick_list, self.update_library_async)

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
        ThreadProgress(thread, _('removing'), '')

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

        self.dstop()

        if(out[0] == 0):
            self.quick_list.remove(self.quick_list[selected])
            
            File(self.lib_file_path).save_json(self.quick_list)
            from .syntax import Syntax
            Syntax()

    def save_installed_list_async(self):
        """Save in thread
        
        Runs the save_installed_list method to avoid block the main
        thread of sublime text
        """

        thread = Thread(target=self.save_installed_list)
        thread.start()
        ThreadProgress(thread, _('processing'), '')

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
        from .syntax import Syntax
        Syntax()

def get_library_folders(platform='all'):
    """Libraries availables
    
    Find the list of all folders that should have libraries.

    The main folders are .platformio/lib who is the global folder
    where platformio stores the libraries installed

    The second one are the libraries inside of the package folder
    .platformio/packages. Each package folder contain a list of
    default libraries, those libraries are selected according to
    the selected option.
    
    Keyword Arguments:
        platform {str} -- platform to search (default: {'all'})
    
    Returns:
        [list] -- list of folders with the libraries
    """
    libraries_folders = []

    pio_packages = getPioPackages(all=True)
    packages_sub_dirs = glob(pio_packages)

    if(platform == 'atmelavr'):
        platform = 'avr'

    for sub_path in packages_sub_dirs:
        if(platform in sub_path or platform == 'all'):
            
            for sub_path in glob(sub_path):
                packages = path.join(sub_path, '*')
                packages = glob(packages)

                for folder in packages:
                    if('libraries' in folder):
                        libraries = path.join(folder, '*')
                        libraries_folders.append(libraries)

    pio_lib_path = getPioLibrary(all=True)
    libraries_folders.insert(0, pio_lib_path)

    # Add the extra folder if it was set by thes user
    extra_folder = get_setting('extra_library', None)
    if(extra_folder):
        extra_folder = path.join(extra_folder, '*')
        libraries_folders.insert(1, extra_folder)

    return libraries_folders

def get_library_list(example_list=False, platform="all"):
    """List of Libraries
    
    Make a list of the libraries availables. This list is
    used in the import library and examples.

    Keyword Arguments:
        example_list {bool} -- if it's True, returns a list of examples 
                                inside of the library (default: {False})

        platform {str} -- results only in the given platform (default: {"all"})
    
    Returns:
        [list/list] -- name of folder and path [[name, path]]
    """
    from re import search

    libraries_folders = get_library_folders(platform)
    
    quick_list = []
    check_list = []

    for library in libraries_folders:
        sub_library = glob(library)

        for content in sub_library:
            caption = path.basename(content)
            new_caption = caption.split("_ID")
            if(new_caption is not None):
                caption = new_caption[0]

            if('__cores__' in content):
                cores = path.join(content, '*')
                cores = glob(cores)

                for sub_core in cores:
                    libs_core = path.join(sub_core, '*')
                    libs_core = glob(libs_core)

                    for lib_core in libs_core:
                        caption = path.basename(lib_core)
                        quick_list.append([caption, lib_core])
                        check_list.append([caption])
                
            if caption not in quick_list and '__cores__' not in caption and caption not in check_list:
                store_data = True
                if(example_list):
                    examples_path = path.join(content, 'examples')
                    store_data = True if path.exists(examples_path) else False
                
                if(store_data):
                    quick_list.append([caption, content])
                    check_list.append(caption)

    return quick_list