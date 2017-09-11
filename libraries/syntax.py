#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path
from threading import Thread

from .file import File
from .libraries import get_library_list
from .tools import accepted_extensions
from .paths import getSyntaxPath, getPluginPath
from ..libraries.thread_progress import ThreadProgress

from ..libraries.I18n import I18n

_ = None

class Syntax(object):
    def __init__(self):
        global _
        _ = I18n().translate

    def check_syntax_file(self):
        """
        Check if the syntax file exits, if not create it
        """
        deviot_syntax = getPluginPath()
        syntax_path = path.join(deviot_syntax, 'deviot.sublime-syntax')
        if(not path.exists(syntax_path)):
            self.create_files_async()

    def set_deviot_syntax(self, view):
        """
        Force sublime text to assign deviot syntax when its
        a iot file
        """

        accepted = accepted_extensions()

        try:
            file = view.file_name()
            ext = file.split(".")[-1]

            if(ext not in accepted):
                return
        except:
            return

        from .paths import getPluginPath, getPluginName

        plugin_name = getPluginName()
        plugin_path = getPluginPath()
        syntax_name = 'deviot.sublime-syntax'
        current_syntax = view.settings().get('syntax')
        deviot_syntax = path.join(plugin_path, syntax_name)

        # check if syntax file was created
        if(not path.exists(deviot_syntax)):
            return

        # assign syntax
        if(not current_syntax.endswith(syntax_name)):
            syntax = 'Packages/{}/{}'.format(plugin_name, syntax_name)
            view.assign_syntax(syntax)

    def paint_iot_views(self):
        """
        Assign the deviot syntax in all iot files
        """
        from sublime import windows
        
        for window in windows():
            for view in window.views():
                self.set_deviot_syntax(view)

    def create_files_async(self):
        """New thread execution
        
        Runs the creation of the files in a new thread
        to avoid block the UI of ST
        """
        from threading import Thread

        thread = Thread(target=self.create_files)
        thread.start()
        ThreadProgress(thread, _('processing'), '')

    def create_files(self):
        """Build files
        
        Create the completions and syntax files.
        It will be stored in the plugin folder
        """
        self.create_syntax()
        self.create_completions()
        self.paint_iot_views()

    def create_syntax(self):
        """sublime-syntax
        
        Expand the C++ highlight syntax with the functios, classes
        constants, etc found in the libraries
        """

        literal1s = ''
        keyword1s = ''
        keyword2s = ''
        keyword3s = ''

        il1 = 0
        ik1 = 0
        ik2 = 0
        ik3 = 0

        keywords = self.get_keywords()
        
        for keys in keywords:
            for word in keys.get_keywords():
                if('LITERAL1' in word.get_type()):
                    literal1s += word.get_id() + '|'
                    if(il1 == 6):
                        literal1s += '\n'
                        il1 = 0
                    il1 += 1
                if('KEYWORD1' in word.get_type()):
                    keyword1s += word.get_id() + '|'
                    if(ik1 == 6):
                        keyword1s += '\n'
                        ik1 = 0
                    ik1 += 1
                if('KEYWORD2' in word.get_type()):
                    keyword2s += word.get_id() + '|'
                    if(ik2 == 6):
                        keyword2s += '\n'
                        ik2 = 0
                    ik2 += 1
                if('KEYWORD3' in word.get_type()):
                    keyword3s += word.get_id() + '|'
                    if(ik3 == 6):
                        keyword3s += '\n'
                        ik3 = 0
                    ik3 += 1

        template_path = getSyntaxPath()
        plugin_path = getPluginPath()
        syntax_path = path.join(plugin_path, 'deviot.sublime-syntax')

        # syntax template
        syntax = File(template_path)
        syntax = syntax.read()

        #replace keywords
        syntax = syntax.replace('{LITERAL1}', literal1s)
        syntax = syntax.replace('{KEYWORD1}', keyword1s)
        syntax = syntax.replace('{KEYWORD2}', keyword2s)
        syntax = syntax.replace('{KEYWORD3}', keyword3s)

        #save new file
        File(syntax_path).write(syntax)

    def create_completions(self):
        """Sublime-completions
        
        Generates the completions file with the keywords extracts from
        the libraries install in the machine
        """
        keyword_ids = ['DEC','OCT','DEC','HEX','HIGH','LOW','INPUT','OUTPUT','INPUT_PULLUP','INPUT_PULLDOWN','LED_BUILTIN']
        keywords = self.get_keywords()

        for keys in keywords:
            for word in keys.get_keywords():
                keyword_ids += [word.get_id() for word in keys.get_keywords()]

        keyword_ids = list(set(keyword_ids))
        completions = {'scope': 'source.iot'}
        completions['completions'] = keyword_ids

        completions_path = getPluginPath()
        completions_path = path.join(completions_path, 'deviot.sublime-completions')

        File(completions_path).save_json(completions)

    def get_keywords(self):
        """Keywords files
        
        Search the keywords.txt file in each library and return
        a list with them.
        
        Returns:
            list -- full path to the keywords.txt
        """
        from ..libraries import keywords

        library_list = get_library_list()

        keywords_list = []
        for library in library_list:
            keyword_file = path.join(library[1], 'keywords.txt')
            if(path.exists(keyword_file)):
                keywords_list.append(keywords.KeywordsFile(keyword_file))

        return keywords_list