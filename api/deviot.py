import sublime

from glob import glob
from os import path, getenv, environ, makedirs, chmod
from collections import OrderedDict
import inspect

_cache = '.cache'
_install_name = 'penv'
_virtualenv_name = 'virtualenv'
VIRTUALENV_URL = 'https://pypi.python.org/packages/source/v/' \
                  'virtualenv/virtualenv-16.0.0.tar.gz'


def version():
    """
    return the plugin version
    """
    version = (2, 3, 0, '.dev7')
    v_format = ".".join([str(s) for s in version[:3]])
    if(len(version) > 3):
        v_format += version[3]
    return v_format


def header():
    """
    header to be used with the request module
    """
    deviot_v = version()
    sublime_v = sublime.version()
    user_agent = 'Deviot/%s (Sublime-Text/%s)' % (deviot_v, sublime_v)
    return {'User-Agent': user_agent}


def create_dirs(dirs):
    """
    Create a specifict path if it doesn't exists
    """
    import errno
    try:
        makedirs(dirs)
    except OSError as exc:
        if exc.errno is not errno.EEXIST:
            raise exc
        pass


def current_file_path():
    """
    full path of the current deviot.py file
    """
    return path.abspath(inspect.getfile(inspect.currentframe()))


def plugin_path():
    """
    path to Packages/Deviot (Arduino IDE)
    """
    current = current_file_path()
    return path.dirname(path.dirname(current))


def plugin_name():
    """
    Name of the plugin ex. Deviot (Arduino IDE)
    """
    plugin = plugin_path()
    return path.basename(plugin)


def packages_path():
    """
    Path to Packages/
    """
    plugin = plugin_path()
    return path.dirname(plugin)


def user_plugin_path():
    """
    Path to Packages/User/Deviot
    """
    packages = packages_path()
    return path.join(packages, 'User', 'Deviot')


def main_menu_path():
    """
    Path to Packages/Deviot/Main.sublime-menu
    """
    plugin = plugin_path()
    return path.join(plugin, 'Main.sublime-menu')


def presets_path():
    """
    Path to Packages/Deviot/presets
    """
    plugin = plugin_path()
    return path.join(plugin, 'presets')


def lang_list_path():
    """
    Path to Packages/Deviot/presets/languages.list
    """
    presets = presets_path()
    return path.join(presets, 'languages.list')


def quick_path():
    """
    Path to Packages/Deviot/presets/quick_panel.json
    """
    presets = presets_path()
    return path.join(presets, 'quick_panel.json')


def context_path():
    """
    Path to Packages/Deviot/presets/context_menu.json
    """
    presets = presets_path()
    return path.join(presets, 'context_menu.json')


def syntax_path():
    """
    Path to Packages/Deviot/presets/template.syntax
    """
    presets = presets_path()
    return path.join(presets, 'template.syntax')


def lang_path():
    """
    Path to Packages/Deviot/languages
    """
    plugin = plugin_path()
    return path.join(plugin, 'languages')


def cache_path():
    """
    Path to Packages/User/Deviot/.cache
    """
    plugin = user_plugin_path()
    return path.join(plugin, _cache)


def preset_file(file_name):
    """
    Path to /Packages/Deviot/presets/filename.json
    """
    presets = presets_path()
    return path.join(presets, file_name)


def temp_path(file_name=False):
    """
    Path to the temp folder depending on the O.S
    """
    tmp_path = '/tmp'
    os_name = sublime.platform()

    if(os_name == 'windows'):
        tmp_path = environ['tmp']

    tmp_path = path.join(tmp_path, 'Deviot')

    if(file_name):
        tmp_path = path.join(tmp_path, file_name)

    return tmp_path


def system_ini_path():
    """
    Path to Packages/User/Deviot/deviot.ini
    """
    user_plugin = user_plugin_path()
    return path.join(user_plugin, 'deviot.ini')


def dependencies_path():
    """
    Path to Packages/User/Deviot/penv
    """
    deviot = user_plugin_path()
    return path.join(deviot, _install_name)


def bin_name():
    """
    Name of the bin folder based on the O.S
    """
    bin = 'bin'
    if('windows' in sublime.platform()):
        bin = 'Scripts'
    return bin


def bin_path():
    """
    Path to Packages/User/Deviot/penv/bin|Scripts
    """
    dependencies = dependencies_path()
    return path.join(dependencies, bin_name())


def pio_penv():
    """
    Path to ~/.platformio/penv/bin
    """
    user_path = path.expanduser('~')
    return path.join(user_path, '.platformio', 'penv', bin_name())


def setting_path():
    """
    Path to Packages/User/Deviot/deviot.ini
    """
    plugin = user_plugin_path()
    return path.join(plugin, 'deviot.ini')


def virtualenv_path():
    """
    Path to Packages/User/Deviot/penv/virtualenv
    """
    dependencies = dependencies_path()
    return path.join(dependencies, _virtualenv_name)


def user_pio_path():
    """
    Path to Packages/User/Deviot/pio
    """
    user_path = user_plugin_path()
    return path.join(user_path, 'pio')


def pio_library(all=False):
    """
    Path to ~/.platformio/lib
    """
    user_path = path.expanduser('~')
    pio_lib = path.join(user_path, '.platformio', 'lib')

    create_dirs(pio_lib)
    chmod(pio_lib, 0o777)

    if(all):
        pio_lib = path.join(pio_lib, '*')

    return pio_lib


def pio_packages(all=True):
    """
    Path to ~/.platformio/packages
    """
    user_path = path.expanduser('~')
    pio_pack = path.join(user_path, '.platformio', 'packages')

    if(all):
        pio_pack = path.join(pio_pack, '*')

    return pio_pack


def boards_file_path():
    """
    Path to Packages/User/Deviot/pio/boards.json
    """
    user_data = user_pio_path()
    return path.join(user_data, 'boards.json')


def libraries_data_path():
    """
    Path to Packages/User/Deviot/pio/libraries.json
    """
    user_data = user_pio_path()
    return path.join(user_data, 'libraries.json')


def virtualenv_list():
    """
    List of elements in VIRTUALENV_URL
    """
    return VIRTUALENV_URL.split('/')


def virtualenv_name():
    """
    Name of the virtualenv folder
    """
    url_list = virtualenv_list()
    list_number = len(url_list)
    return url_list[list_number - 1]


def virtualenv_file():
    """
    Path to Packages/User/Deviot/.cache/virtualenv
    """
    cache = cache_path()
    return path.join(cache, virtualenv_name())


def get_sysetting(key, default=None):
    """
    Stores the setting in the file:
    Packages/User/Deviot/deviot.ini
    """
    from ..libraries.readconfig import ReadConfig

    section = "config"
    setting_file = setting_path()

    config = ReadConfig()

    # remove config file if it's currupted
    if(config.bad_format()):
        ini = path.join(packages_path, 'User', 'Deviot', 'deviot.ini')

        if(path.exists(ini)):
            remove(ini)

    config.read(setting_file)

    if(not config.has_option(section, key)):
        return default

    output = config.get(section, key)[0]

    if(output == 'True' or output == 'False'):
        output = True if output == 'True' else False

    return output


def save_sysetting(key, value):
    """
    Gets the setting stored in the file
    Packages/User/Deviot/deviot.ini
    """
    from ..libraries.readconfig import ReadConfig

    section = "config"
    setting_file = setting_path()

    create_dirs(path.dirname(setting_file))

    config = ReadConfig()
    config.read(setting_file)

    if(not config.has_section(section)):
        config.add_section(section)

    config.set(section, key, value)

    with open(setting_file, 'w') as configfile:
        config.write(configfile)


def prepare_command(command):
    """
    Edit the command depending of the O.S of the user
    """
    bin_dir = bin_path()
    platform = sublime.platform()
    deviot_bin = get_sysetting('deviot_bin', False)
    env_paths = get_sysetting('env_path', False)
    symlink = get_sysetting('symlink', 'python')

    if(not path.exists(bin_dir) or bool(deviot_bin) or
       not env_paths and platform == 'windows'):
        return command

    if(platform == 'osx'):
        exe = symlink
        options = ['-m', command[0]]
    else:
        exe = command[0]
        options = []

    executable = path.join(bin_dir, exe)

    cmd = ['"%s"' % (executable)]
    cmd.extend(options)
    cmd.extend(command[1:])

    return cmd


def pio_command(options, verbose=False):
    """
    Completes PlatformIO command
    """
    cmd = " ".join(options)
    command = prepare_command(['platformio', '-f', '-c', 'sublimetext'])
    command.extend(options)

    # verbose mode
    if(verbose and 'run' in cmd and '-e' in cmd):
        command.extend(['-v'])
    return command


def run_command(command, cwd=None, env_paths=False):
    '''Commands

    Run all the commands to install the plugin

    Arguments:
        command {list} -- list of commands

    Keyword Arguments:
        cwd {str} -- current working dir (default: None)
        prepare_cmd {bool} -- when is true the platformIO command will
                          be updated to be multi-platform compatible
                          (default: False)

    Returns:
        [list] -- list[0]: return code list[1]: command output
    '''
    import subprocess

    # defining default env paths
    if(env_paths):
        environ['PATH'] = env_paths

    command.append("2>&1")
    command = ' '.join(command)

    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, cwd=cwd,
                               universal_newlines=True, shell=True)

    output = process.communicate()
    stdout = output[0]
    return_code = process.returncode

    return (return_code, stdout)


def environment_paths():
    '''Environment

    All the necessary environment paths are merged to run platformIO
    correctly

    Returns:
        [list] -- paths in a list
    '''
    # default paths
    default = default_paths()
    system = environ.get("PATH", "").split(path.pathsep)

    env_paths = []
    env_paths.extend(default)
    env_paths.extend(system)

    env_paths = list(OrderedDict.fromkeys(env_paths))
    env_paths = path.pathsep.join(env_paths)

    return env_paths


def default_paths():
    """Python Paths

    Folder where python should be installed in the diferents os

    Returns:
        list -- paths corresponding to the os
    """
    if(sublime.platform() == 'windows'):
        default_paths = ["C:\\Python27", "C:\\Python27\\Scripts"]
    else:
        user_bin_path = path.join(path.expanduser('~'), '.local', 'bin')
        default_paths = ["/usr/bin", "/usr/local/bin", user_bin_path]

    # possible old installation in /Packages/User/Deviot
    default_paths.append(bin_path())

    # instalation from atom or MS VS
    default_paths.append(pio_penv())

    # get path from python.txt in Packages/User/Deviot
    packages = packages_path()
    deviot_path = path.join(packages, 'User', 'Deviot')
    extra_python = path.join(deviot_path, 'python.txt')

    if(path.exists(extra_python)):
        with open(extra_python) as file:
            for line in file:
                line = line.strip()
                new_path = path.normpath(line)
                default_paths.append(new_path)

    temp_path = default_paths
    default_paths = []

    for tpath in temp_path:
        if(path.exists(tpath)):
            default_paths.append(tpath)

    return default_paths


def listWinVolume():
    """
    return the list of system drives in windows
    """
    vol_list = []
    for label in range(65, 90):
        vol = chr(label) + ':\\'
        if(path.isdir(vol)):
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
        home_path = getenv('HOME')
        root_list = [home_path, 'System Root(/)']
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
    path = path.join(path, '*')
    return glob(path)


def folder_explorer(path=None, callback=None, key=None, plist=None, index=-2):
    """Explore a path

    Using the quick panel, this fuction allows the user to select a path, it
    will be always a folder.

    When you give a path in the 'path' argument, the explorer will be open it
    in the given path. If you don't pass any path, the 'last_path' setting
    will be check to open the explorer in the last path used. If not path is
    found it will show the root path.

    Callbak is the function that is executed when the 'select current path'
    option is selected when the 'key' argument is given the callback will be
    called like callbak(key, path) if there is not key; callback(path). (The
    key argument is useful to work with the preferences)

    The rest of the arguments are used by the fuction and you don't need worry
    about it

    Keyword Arguments:
        path {str} -- stores the current path selected (default: None)
        callback {function} -- called when a folder is selected (default: None)
        key {str} -- key to use in the callback (default: {None})
        plist {list} -- list of path handled by the function (default: None)
        index {number} -- index of the last selection (default: -2)

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
        prev = path.dirname(path)
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

    sublime.set_timeout(
        lambda: quick_panel(
            paths_list, lambda index: folder_explorer(
                path, callback, key, paths_list, index)), 0)
