#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import glob
import errno
import inspect
import sublime

ROOT_PATH = 'System Root(/)'

current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))


def listWinVolume():
    """
    return the list of system drives in windows
    """
    vol_list = []
    for label in range(67, 90):
        vol = chr(label) + ':\\'
        if os.path.isdir(vol):
            vol_list.append(vol)
    return vol_list


def list_root_path():
    """
    return the system drives in windows or unix
    """
    root_list = []
    os_name = sublime.platform()
    if os_name == 'windows':
        root_list = listWinVolume()
    else:
        home_path = os.getenv('HOME')
        root_list = [home_path, ROOT_PATH]
    return root_list

def globalize(path):
    """Apply Glob
    
    List all files/folders in the given path and return
    a list with the results
    
    Arguments:
        path {str} -- folder path
    
    Returns:
        [list] -- list with all file/folder inside the path
    """
    path = os.path.join(path, '*')
    globalize = glob.glob(path)

    return globalize

def folder_explorer(path=None, callback=None, key=None, plist=None, index=-2):
    """Explore a path
    
    Using the quick panel, this fuction allows the user to select a path, it will be always
    a folder.

    When you give a path in the 'path' argument, the explorer will be open it in the
    given path. If you don't pass any path, the 'last_path' setting will be check to
    open the explorer in the last path used. If not path is found it will show the
    root path.

    Callbak is the function that is executed when the 'select current path' option is selected
    when the 'key' argument is given the callback will be called like callbak(key, path) if
    there is not key; callback(path). (The key argument is useful to work with the preferences)

    The rest of the arguments are used by the fuction and you don't need worry about it
    
    Keyword Arguments:
        path {str} -- stores the current path selected (default: {None})
        callback {function} -- callback called when a folder is selected (default: {None})
        key {str} -- key to use in the callback (default: {None})
        plist {list} -- list of path handled by the function (default: {None})
        index {number} -- index of the last selection (default: {-2})
    
    Returns:
        [function] -- callback with the selected path
    """

    if(index == -1):
        return

    # close if can't back anymore
    if(not path and index == 1):
        return

    # last path used
    if(not path):
        from .tools import get_setting
        path = get_setting('last_path', None)

    from .I18n import I18n
    _ = I18n().translate

    paths_list = []

    # recognize path
    if(path and not plist):
        index = -3
        new_path = globalize(path)
        paths_list.extend(new_path)

    # back
    if(index == 1 and path):
        plist = globalize(path)
        prev = os.path.dirname(path)
        back_list = globalize(prev)
        if(path == prev):
            index = -2
            path = None
            plist = None
        else:
            paths_list.extend(back_list)
            path = prev

    # select current
    if(index == 0):
        # store last path used
        from .tools import save_setting
        save_setting('last_path', path)

        if(not key):
            return callback(path)
        return callback(key, path)

    if(plist and index != 1):
        path = plist[index]

    path_caption = path if(path) else "0"
    paths_list.insert(0, _("select_{0}", path_caption))
    paths_list.insert(1, _("_previous"))

    # start from root
    if(index == -2):
        root_list = list_root_path()
        paths_list.extend(root_list)
    # iterate other path
    elif(index > 1):
        new_path = globalize(plist[index])
        paths_list.extend(new_path)

    from .quick_panel import quick_panel

    sublime.set_timeout(lambda: quick_panel(paths_list, lambda index: folder_explorer(path, callback, key, paths_list, index)), 0)