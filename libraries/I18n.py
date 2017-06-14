#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Translate the plugin
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from .paths import getLangListPath, getLangPath
from .tools import singleton, get_setting, save_setting
from os import path
from .file import File
from glob import glob

@singleton
class I18n(object):
    def __init__(self):
        self.sys_lang = None
        self.lang_list = {}
        self.lang_params = {}
        self.ids_lang = []
        self.id_name_dict = {}
        self.translations = {}
        self.lang_list = {}

        self.get_system_lang()
        self.set_lang()

    def translate(self, text, *params):
        """Trnaslate string
        
        Translate the text string in the selected language (in the UI
        of the plugin) and return it
        
        Arguments:
            text {str} -- text to translate
            *params {[type]} -- [description]
        
        Returns:
            str -- text translated
        """
        translated = self.translations.get(text, text)

        for seq, param in enumerate(params):
            seq_text = '{%d}' % seq
            translated = translated.replace(seq_text, str(param))

        return translated

    def set_lang(self):
        """Set Language
        
        Sets the language that will be used in the plugin. If there is none option
        in the preferences file, the system language will be used
        
        Arguments:
            selection {str} -- ISO 639*1 language string
        """
        selection = get_setting('lang_id', self.sys_lang)
        
        self.get_lang_files()
        
        lang = selection if(self.sys_lang in self.id_name_dict) else 'en'
        file_path = self.id_name_dict[lang]
        lang_file = TranslatedLines(file_path)
        
        self.translations = lang_file.translte_text()
        save_setting('lang_id', lang)

    def get_lang_ids(self):
        """Language ids lists
        
        List of the language ids (en, es, fr, etc)
        
        Returns:
            list -- list with ids
        """
        return self.ids_lang

    def get_lang_name(self, lang_id):
        """Full Language Name
        
        Given the ISO 639*1 language name, it will return the name of the language
        firs in english and the second in the language itself
        
        Arguments:
            lang_id {str} -- ISO 639*1 language name
        
        Returns:
            list -- names of the language
        """
        self.get_lang_list()

        return self.lang_list.get(lang_id, ['Unknown', 'Unknown'])

    def get_lang_list(self):
        """Language List
        
        Get a list with all languages, the main file is located in
        deviot/presets/language.list
        """
        file_path = getLangListPath()
        file = File(file_path)

        self.lang_list = file.read_json()

    def get_lang_files(self):
        """Available Languages
        
        Finds all the languages availables in deviot, the language (translated) files
        are located in Deviot/languages/nn.lang.

        NOTE: the language file MUST be in the ISO 639*1 format (two letters) and must have
        the extension .lang
        """
        lang_path = getLangPath()
        lang_paths = glob(lang_path + '/*.lang')
        lang_file_names = [path.basename(file_path) for file_path in lang_paths] # es.lang
        ids_lang = [path.splitext(name)[0] for name in lang_file_names] # es
        self.id_name_dict.update(dict(zip(ids_lang, lang_paths))) #{"es": 'path/es.lang'}
        ids_lang.sort() # order list
        self.ids_lang = ids_lang
        

    def get_system_lang(self):
        """System Language
        
        Get the language of the system (O.S)
        """
        from locale import getdefaultlocale

        sys_language = getdefaultlocale()[0]
        if not sys_language:
            sys_language = 'en'
        else:
            sys_language = sys_language.lower()

        self.sys_lang = sys_language[:2]


class TranslatedLines(File):
    def __init__(self, file_path):
        super(TranslatedLines, self).__init__(file_path)
        self.lang_lines = self.read()

    def translte_text(self):
        """Translate Text
        
        Translate the text loaded in the lang_lines object.
        It returns the strins without comments

        Returns:
            dict -- dictionaty with the translate strings
        """
        new_dict = {}
        lines = self.lang_lines.split('\n')
        lines = [line.strip() for line in lines if lines if line.strip() and
                not line.strip().startswith('#')]
        blocks = self.split_lines(lines)

        for block in blocks:
            key, value = self.sanitize(block)
            new_dict[key] = value

        return new_dict


    def split_lines(self, lines):
        """Split Lines
        
        Splits the msgid from the msgstr
        
        Arguments:
            lines {list} -- list with all strings
        
        Returns:
            list -- string separated
        """
        block, blocks = [], []
        
        for line in lines:
            if line.startswith('msgid'):
                blocks.append(block)
                block = []
            block.append(line)
        
        blocks.append(block)
        blocks.pop(0)
        
        return blocks

    def sanitize(self, block):
        """Clean Strins
        
        Remove msgstr: and msgid: from the strings
        
        Arguments:
            block {list} -- strigns with msgid and msgstr
        """
        is_key, key, value = True, '', ''
        
        for line in block:
            index = line.index('"')
            clean_line = line[index + 1: -1]
            
            if line.startswith('msgstr'):
                is_key = False
            if is_key:
                key += clean_line
            else:
                value += clean_line
        
        return (key, value)
