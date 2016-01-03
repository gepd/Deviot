#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Documents
#

"""
Documents
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import glob

from . import Paths
from . import Tools
from .Preferences import Preferences
from .JSONFile import JSONFile


@Tools.singleton
class I18n(object):

    def __init__(self):
        self.lang_params = {}
        self.lang_ids = []
        self.id_path_dict = {}
        self.trans_dict = {}
        self.list_ids()
        self.Preferences = Preferences()
        self.lang_id = self.Preferences.get('lang_id', Tools.getSystemLang())
        self.change_lang(self.lang_id)

    def list_ids(self):
        language_list_path = Paths.getLanguageList()
        self.lang_params = JSONFile(language_list_path).getData()
        language_path = Paths.getLanguagePath()

        lang_file_paths = glob.glob(language_path + '/lang_*.txt')
        lang_file_names = [os.path.basename(p) for p in lang_file_paths]
        self.lang_ids += [name[5:-4] for name in lang_file_names]
        self.id_path_dict.update(dict(zip(self.lang_ids, lang_file_paths)))
        self.lang_ids.sort(key=lambda _id: self.lang_params.get(_id)[1])

    def change_lang(self, lang_id):
        if lang_id in self.id_path_dict:
            self.lang_id = lang_id
            lang_file_path = self.id_path_dict[lang_id]
            lang_file = LanguageFile(lang_file_path)
            self.trans_dict = lang_file.get_trans_dict()
        else:
            self.lang_id = 'en'
            self.trans_dict = {}
        self.Preferences.set('lang_id', self.lang_id)

    def translate(self, text, *params):
        trans_text = self.trans_dict.get(text, text)
        for seq, param in enumerate(params):
            seq_text = '{%d}' % seq
            trans_text = trans_text.replace(seq_text, str(param))
        return trans_text

    def get_lang_id(self):
        return self.lang_id

    def get_lang_ids(self):
        return self.lang_ids

    def get_lang_names(self, lang_id):
        return self.lang_params.get(lang_id, ['Unknown', 'Unknown'])


class LanguageFile(JSONFile):

    def __init__(self, path):
        super(LanguageFile, self).__init__(path)
        text = self.readFile()
        self.trans_dict = load_trans_dict(text)

    def get_trans_dict(self):
        return self.trans_dict


def load_trans_dict(text):
    trans_dict = {}
    lines = text.split('\n')
    lines = [line.strip() for line in lines if lines if line.strip() and
             not line.strip().startswith('#')]
    blocks = split_lines(lines)
    for block in blocks:
        key, value = load_trans_pair(block)
        trans_dict[key] = value
    return trans_dict


def split_lines(lines):
    block, blocks = [], []
    for line in lines:
        if line.startswith('msgid'):
            blocks.append(block)
            block = []
        block.append(line)
    blocks.append(block)
    blocks.pop(0)
    return blocks


def load_trans_pair(block):
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
