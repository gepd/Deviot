#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import glob

try:
    from . import Paths
    from . import Tools
    from .Preferences import Preferences
    from .JSONFile import JSONFile
except:
    from libs import Paths
    from libs import Tools
    from libs.Preferences import Preferences
    from libs.JSONFile import JSONFile


@Tools.singleton
class I18n(object):

    def __init__(self):
        self.lang_params = {}
        self.ids_lang = []
        self.id_path_dict = {}
        self.trans_dict = {}
        self.listIds()
        self.Preferences = Preferences()
        self.id_lang = self.Preferences.get('id_lang', Tools.getSystemLang())
        self.changeLang(self.id_lang)

    def listIds(self):
        language_list_path = Paths.getLanguageList()
        self.lang_params = JSONFile(language_list_path).getData()
        language_path = Paths.getLanguagePath()

        lang_file_paths = glob.glob(language_path + '/*.lang')
        lang_file_names = [os.path.basename(p) for p in lang_file_paths]
        self.ids_lang += [os.path.splitext(nam)[0] for nam in lang_file_names]
        self.id_path_dict.update(dict(zip(self.ids_lang, lang_file_paths)))
        self.ids_lang.sort(key=lambda _id: self.lang_params.get(_id)[1])

    def changeLang(self, lang_id):
        self.id_lang = lang_id if(lang_id in self.id_path_dict) else 'en'
        lang_file_path = self.id_path_dict[self.id_lang]
        lang_file = LanguageFile(lang_file_path)
        self.trans_dict = lang_file.getTransDict()
        self.Preferences.set('id_lang', self.id_lang)

    def translate(self, text, *params):
        trans_text = self.trans_dict.get(text, text)
        for seq, param in enumerate(params):
            seq_text = '{%d}' % seq
            trans_text = trans_text.replace(seq_text, str(param))
        return trans_text

    def getLangId(self):
        return self.id_lang

    def getLangIds(self):
        return self.ids_lang

    def getLangNames(self, lang_id):
        return self.lang_params.get(lang_id, ['Unknown', 'Unknown'])


class LanguageFile(JSONFile):

    def __init__(self, path):
        super(LanguageFile, self).__init__(path)
        text = self.readFile()
        self.trans_dict = loadTransDict(text)

    def getTransDict(self):
        return self.trans_dict


def loadTransDict(text):
    trans_dict = {}
    lines = text.split('\n')
    lines = [line.strip() for line in lines if lines if line.strip() and
             not line.strip().startswith('#')]
    blocks = splitLines(lines)
    for block in blocks:
        key, value = loadTransPair(block)
        trans_dict[key] = value
    return trans_dict


def splitLines(lines):
    block, blocks = [], []
    for line in lines:
        if line.startswith('msgid'):
            blocks.append(block)
            block = []
        block.append(line)
    blocks.append(block)
    blocks.pop(0)
    return blocks


def loadTransPair(block):
    is_key, key, value = True, '', ''
    for line in block:
        index = line.index('"')
        cur_str = line[index + 1: -1]
        if line.startswith('msgstr'):
            is_key = False
        if is_key:
            key += cur_str
        else:
            value += cur_str
    return (key, value)
