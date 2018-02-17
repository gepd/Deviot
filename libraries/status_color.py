# MIT License
#
# Copyright (c) 2017 GEPD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# HOW TO USE
#
# import status_color
#
# // sets a color. Possibles values ("error", "success", "warning")
# status_color.set("error")
#
# // removes the color
# status_color.remove()
#
# // sets a color and remove it after 5 seconds
# status_color.set("error", 5000)


import sublime
from glob import glob
from errno import EEXIST
from os import path, makedirs, remove as remove_file

# color definition
# edit this var to remove or add your own colors
# [[backgrond_color], [text_color]]
colors = {
    'error': [[200, 50, 60], [230, 230, 230]],
    'success': [[50, 170, 60], [230, 230, 230]],
    'warning': [[200, 140, 40], [230, 230, 230]]
}

theme_path = None


def set(status=False, timeout=0):
    """Set color in the status status

    Sets the given action as color in the status bar

    Keyword Arguments:
        status {bool} -- sets a color in the status bar based on the actions
                        defined in the 'colors' global var. (default: {False})
        timeout {number} -- removes the status bar color after the given delay
                        in milliseconds. If not defined the color will keep
                        forever (default: {0})
    """
    global theme_path

    check_folder_paths()

    resource = []
    # background color
    resource.append({"class": "status_bar", "layer0.tint": colors[status][0]})
    # text color
    resource.append({"class": "label_control", "color": colors[status][1]})
    resource = sublime.encode_value(resource)

    # save file
    with open(theme_path, 'w') as file:
        file.write(resource)

    if(timeout > 0):
        sublime.set_timeout_async(remove, timeout)


def remove(remove_path=None):
    """Remove status bar color

    Removes the file that overrides the theme status bar color
    """
    if(remove_path):
        from shutil import rmtree
        if(path.exists(remove_path)):
            rmtree(remove_path)
        return

    try:
        if(path.exists(theme_path)):
            remove_file(theme_path)
    except:
        pass


def check_folder_paths():
    """Check folder and theme path

    Checks the status_color folder exitence and sets the full path
    of the curren theme
    """
    global theme_path

    setting = sublime.load_settings("Preferences.sublime-settings")
    theme_name = setting.get("theme")

    packages = sublime.packages_path()
    user_path = path.join(packages, 'User')
    theme_folder = path.join(user_path, 'Status Color')

    # create folder
    if(not path.exists(theme_folder)):
        try:
            makedirs(theme_folder)
        except OSError as exc:
            pass

    theme_path = path.join(theme_folder, theme_name)
