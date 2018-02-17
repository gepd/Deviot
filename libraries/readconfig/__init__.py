#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2017 gepd@outlook.com

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

author: gepd
website: https://github.com/gepd/ReadConfig
library version: 0.0.5
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
from os import path
from collections import OrderedDict

ENCODING = 'latin-1'

class ReadConfig(object):
    """Configuration file parser.

    A configuration file consists of sections, lead by a "[section]" header,
    and followed by "name = value" entries

    class:

    ReadConfig -- responsible for parsing a list of
                  configuration files, and managing
                  the parsed database.
    """

    comment_prefixes = ('#', ';')

    # Parsing regular expressions

    # Section regex
    _SECTION_PATT = r"""
    \[
    [a-zA-Z0-9:*_-]+        # letters, numbers and :-_ simbols
    \]"""

    # option regex
    _OPTION_PATT = r'(([\w]+)\s*\=? (.+)|)'

    # value regex
    _VALUE_PATT = r'(([\w]+\s=*\s*)? (.+)|)'

    # Compiled regular expression for matching sections
    SECTCRE = re.compile(_SECTION_PATT, re.VERBOSE)

    # Compiled regular expression for matching options
    OPTRE = re.compile(_OPTION_PATT)

    # Compiled regular expression for matching values
    VALRE = re.compile(_VALUE_PATT, re.VERBOSE)

    # Compiled regular expression for remove square brakets
    _KEYCRE = re.compile(r"\[|\]")

    def __init__(self):
        # data stored
        self._comment_count = 0
        self._break_count = 0
        self._data = OrderedDict()
        self._sections = []
        self._cur_sect = None
        self._cur_opt = None
        self._in_option = False
        self._new_sect = []
        self._new_opts = OrderedDict()
        self._bad_format = False

    def read(self, filepath):
        """
        Read the given file (if it exists)
        """
        if(not path.exists(filepath)):
            return False

        with open(filepath, 'rb') as file:
            for line in file:

                line = line.decode(ENCODING)

                # store breaklines
                self._breakline(line)
                # store comments
                self._comments(line)
                # store sections
                self._raw_sections(line)
                # store options
                self._raw_options(line)
                # stop if file has a bad format
                if(self._bad_format):
                    break
                # store values
                self._raw_values(line)

    def _breakline(self, line):
        """
        Store breakline(s) of the source file
        """
        if(line == '\r\n' or line == '\n'):
            key = "${0}".format(self._break_count)
            self._data[key] = '\n'
            self._break_count += 1

    def _comments(self, line):
        """
        Store comments of the source file
        """
        if(line.startswith(ReadConfig.comment_prefixes) and not self._cur_sect):
            key = '#{0}'.format(self._comment_count)
            self._data[key] = line.rstrip()
            self._comment_count += 1

    def _raw_sections(self, line):
        """
        Extract the section(s)
        """
        is_section = self.SECTCRE.match(line)
        if(is_section):
            section = self._KEYCRE.sub('', line).rstrip()
            self._data[section] = OrderedDict()
            self._cur_sect = section
            self._sections.append(section)
            self._in_option = False
    
    def _raw_options(self, line):
        """
        Extract the option(s)
        """
        is_option = self.OPTRE.match(line)
        if(is_option):
            option = is_option.group(2)
            if(option):
                section = self._cur_sect
                if(not section):
                    self._bad_format = True
                    return
                self._data[section][option] = []
                self._cur_opt = option
                self._in_option = True

    def _raw_values(self, line):
        """
        Extract the value(s)
        """
        if(self._in_option):
            is_value = self.VALRE.match(line)
            if(is_value):
                section = self._cur_sect
                option = self._cur_opt
                value = is_value.group(3)
                value = value if value else line
                value = value.rstrip()
                if(value and not value.startswith('=')):
                    self._data[section][option].append(value)
    
    def bad_format(self):
        """
        Checks if the readed file is well formatted or not.
        Will be considered a bad format, if a section header isn't present.
        True if the file is bad formatted, False if not
        """
        return self._bad_format

    def add_section(self, section):
        """
        Add a section named section to the instance. If a section by the
        given name already exists, will return false
        """
        if(section not in self._sections):
            self._new_sect.append(section)
            self._sections.append(section)
            return True
        return False

    def set(self, section, option, value):
        """
        If the given section exists, set the given option to the specified
        value; otherwise will return false. each argument expects a string
        """
        value = str(value)
        if(section in self._data):
            self._data[section][option] = [value]
            return True
        elif(section in self._new_sect):
            if(section not in self._data):
                self._data[section] = OrderedDict()
            self._data[section][option] = [value]
            return True
        else:
            return False

    def get(self, section, option):
        """
        Get an option value for the named section.
        """
        if(section in self._sections):
            if(option in self._data[section].keys()):
                values = []
                for op in self._data[section][option]:
                    if(not op.startswith('#')):
                        values.append(op)

                if(len(values) > 1):
                    return values
                else:
                    return values
        return False

    def has_section(self, section):
        """
        Checks if the named section is present  or not.
        """
        return section in self._sections

    def has_option(self, section, option):
        """
        Checks if the named option is present  or not.
        """
        if(section not in self._sections):
            return False
        return option in self._data[section].keys()

    def sections(self):
        """
        Return a list of the sections available
        """
        return self._sections

    def options(self, section):
        """
        Returns a list of options available in the specified section
        """
        if(self.has_section(section)):
            return self._data[section].keys()
        return False

    def remove_section(self, section):
        """
        Remove the specified section from the configuration. If the
        section in fact existed, return True. Otherwise return False.
        """
        if(section in self._sections):
            del self._data[section]
            self._sections.remove(section)
            return True
        return False

    def remove_option(self, section, option):
        """
        Remove the specified option from the specified section. If
        the section does not exist, it will return None. Otherwise
        will return false if the option do not exist and True if
        it's removed.
        """
        if(section in self._sections):
            if(option in self._data[section]):
                del self._data[section][option]
                return True
            return False
        return None

    def write(self, fileobject):
        """
        Write a representation of the configuration to the specified
        file object.
        """
        new_data = '' # where file will be stored

        for linedata in self._data:
            line = self._data[linedata]
 
            if(type(line) is type(str())):
                # comment(s)
                if(line.startswith(ReadConfig.comment_prefixes)):
                    new_data  += line + '\n'
                # break line(s)
                else:
                    new_data += '\n'
            else:
                # header(s)
                new_data  += '[{0}]\n'.format(linedata)

                # option(s) - value(s)
                for key, values in line.items():
                    comcount = [x for x in values if x.startswith('#')]
                    if(len(values) > 1):
                        values = "\n".join(values)
                        if(len(comcount) == 0):
                            values = '\n' + values
                        else:
                            values = ' ' + values
                        new_data += '{0} ={1}\n'.format(key, values)
                    else:
                        new_data += '{0} = {1}\n'.format(key, values[0])

        # write in file
        fileobject.write(new_data)