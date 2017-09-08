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

    def create_syntax(self):
        """sublime-syntax
        
        Expand the C++ highlight syntax with the functios, classes
        constants, etc found in the libraries
        """

        literal1s = []
        keyword1s = []
        keyword2s = []
        keyword3s = []

        keywords = self.get_keywords()
        
        for keys in keywords:
            for word in keys.get_keywords():
                if('LITERAL1' in word.get_type()):
                    literal1s.append(word.get_id())
                if('KEYWORD1' in word.get_type()):
                    keyword1s.append(word.get_id())
                if('KEYWORD2' in word.get_type()):
                    keyword2s.append(word.get_id())
                if('KEYWORD3' in word.get_type()):
                    keyword3s.append(word.get_id())

        # convert to string
        literal1s = set(literal1s)
        literal1s = "|".join(literal1s)

        keyword1s = set(keyword1s)
        keyword1s = "|".join(keyword1s)

        keyword2s = set(keyword2s)
        keyword2s = "|".join(keyword2s)

        keyword3s = set(keyword3s)
        keyword3s = "|".join(keyword3s)

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