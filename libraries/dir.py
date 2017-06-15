from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import glob


class Dir(object):

    def __init__(self, path):
        path = os.path.abspath(path)
        self.set_path(path)

    def __str__(self):
        return '%s (%s)' % (self.name, self.path)

    def set_path(self, path):
        self.path = path
        self.dir = os.path.dirname(self.path)
        self.name = os.path.basename(self.path)
        self.caption = self.name

    def get_path(self):
        return self.path

    def get_name(self):
        return self.name

    def is_temp_file(self):
        state = False
        lower_name = self.name.lower()
        if lower_name == 'cvs':
            state = True
        elif lower_name.startswith('$') or lower_name.startswith('.'):
            state = True
        elif lower_name.endswith('.tmp') or lower_name.endswith('.bak'):
            state = True
        return state

    def is_dir(self):
        return os.path.isdir(self.path)

    def list_alls(self, pattern='*'):
        all_files = []
        paths = glob.glob(os.path.join(self.path, pattern))
        all_files = (Dir(path) for path in paths)
        all_files = [f for f in all_files if not f.is_temp_file()]
        all_files.sort(key=lambda f: f.get_name().lower())
        return all_files

    def list_dirs(self, pattern='*'):
        all_files = self.list_alls(pattern)
        dirs = [Dir(f.path) for f in all_files if f.is_dir()]
        return dirs
