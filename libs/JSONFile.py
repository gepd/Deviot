#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import json
import codecs


class JSONFile(object):
    '''
    This class allows to load and save JSON files
    '''

    def __init__(self, path):
        '''
        This construct loads a file when is called and
        load the information in a global object

        Arguments: path {string} -- Full path of the JSON file
        '''
        super(JSONFile, self).__init__()
        self.setEncoding()
        self.data = {}
        self.path = path
        self.loadData()

    def loadData(self):
        '''
        Load the content of a JSON file and
        deserialize it to set the information
        in a global object called data
        '''
        try:
            text = self.readFile()
        except:
            return

        try:
            self.data = json.loads(text)
        except:
            pass

    def getData(self):
        '''
        It's an alternative way to get the data obtained from
        the JSON file. The other way is using only the 'data'
        global object.

        Returns: {miltiple} -- mutiple type of data stored in the
                                                differents files.
        '''
        return self.data

    def setData(self, data):
        '''
        Save the data in the file setted on the
        construct. This method is most used in
        the preferences class.

        Arguments: data {string} -- data to save in the JSON file.
        '''
        self.data = data
        self.saveData()

    def saveData(self):
        '''
        Serialize the data stored in the global object data
        and call to Write file. This function is called automatically
        when any data is set in the method SetData.

        '''
        text = json.dumps(self.data, sort_keys=True, indent=4)
        self.writeFile(text)

    def readFile(self):
        '''
        Read the data from the file specified in the global object path.
        The data readed is encoded with the format specified in the global
        object encoding, by default this object is UTF-8. Use this method
        if you don't want to modify the data received from the file.

        Returns: text {string} -- encoded text readed from file
        '''
        text = ''

        try:
            with codecs.open(self.path, 'r', self.encoding) as file:
                text = file.read()
        except (IOError, UnicodeError):
            pass

        return text

    def writeFile(self, text, append=False):
        '''Write File

        Write the data passed in a file specified in the global object path.
        This method is called automatically by saveData, and encode the text
        in the format specified in the global object encoding, by default this
        object is UTF-8. Use this method if you don't want to modify the data
        to write.

        Arguments: text {string} -- Text to write in the file
                   append {boolean} -- Set to True if you want to append the
                   data in the file (default: False)
        '''
        mode = 'w'

        if append:
            mode = 'a'
        try:
            with codecs.open(self.path, mode, self.encoding) as file:
                file.write(text)
        except (IOError, UnicodeError):
            pass

    def setEncoding(self, encoding='utf-8'):
        '''
        Call this method to change the format to encode the files when you
        load it or save it.

        Keyword Arguments: encoding {string} -- Format to encoding
                                                    default: UTF-8
        '''
        self.encoding = encoding
