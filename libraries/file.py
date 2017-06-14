# !/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

class File(object):

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self, text):
        """Write File
        
        Writes the content of text in the file set in self.file_name
        
        Arguments:
            text {str} -- text to write
        
        Returns:
            bool -- true if was writed succesuflly
        """
        with open(self.file_name, 'w') as file:
            file.write(text)
            return True

    def read(self):
        """Read File
        
        returns the content of the file set in self.file_name
        
        Returns:
            str -- string from file
        """
        encoding = 'utf-8'
        text = ''

        try:
            with codecs.open(self.file_name, 'r', encoding) as file:
                text = file.read()
        except(IOError, UnicodeError):
            pass
        return text

    def read_json(self):
        """read JSON
        serialize the content of the file and transform it in
        a json format type
        
        Returns:
            JSON -- serialized json data
        """
        from json import loads

        file = self.read()
        json = loads(file)

        return json

    def save_json(self, text):
        """Save JSON
        
        Stores JSON data in a file, before do it deserialize
        
        Arguments:
            text {str} -- json data to stored
        """
        from json import dumps
        
        text = dumps(text, sort_keys=True, indent=4)
        self.write(text)
