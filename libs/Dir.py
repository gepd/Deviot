from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import glob
import codecs


class Dir(object):

    def __init__(self, path):
        path = os.path.abspath(path)
        self.setPath(path)

    def setPath(self, path):
        self.path = path
        self.dir = os.path.dirname(self.path)
        self.name = os.path.basename(self.path)
        self.caption = self.name

    def __str__(self):
        return '%s (%s)' % (self.name, self.path)

    def getPath(self):
        return self.path

    def getName(self):
        return self.name

    def isTempFile(self):
        state = False
        lower_name = self.name.lower()
        if lower_name == 'cvs':
            state = True
        elif lower_name.startswith('$') or lower_name.startswith('.'):
            state = True
        elif lower_name.endswith('.tmp') or lower_name.endswith('.bak'):
            state = True
        return state

    def isDir(self):
        return os.path.isdir(self.path)

    def listAll(self, pattern='*'):
        all_files = []
        paths = glob.glob(os.path.join(self.path, pattern))
        all_files = (Dir(path) for path in paths)
        all_files = [f for f in all_files if not f.isTempFile()]
        all_files.sort(key=lambda f: f.getName().lower())
        return all_files

    def listDirs(self, pattern='*'):
        all_files = self.listAll(pattern)
        dirs = [Dir(f.path) for f in all_files if f.isDir()]
        return dirs
