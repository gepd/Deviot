# !/usr/bin/env python
# -*- coding: utf-8 -*-


class File(object):

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self, text):
        """
        write the content of text in the file set in self.file_name
        """
        with open(self.file_name, 'w') as file:
            file.write(text)

    def read(self):
        """
        return the content of the file set in self.file_name
        """
        with open(self.file_name) as file:
            return file.read()

    def get_in_json(self):
        """
        serialize the content of the file and transform it in
        a json format type
        """
        from json import loads

        file = self.read()
        json = loads(file)

        return json
