import sublime
import sublime_plugin

from os import path, environ, makedirs
from collections import OrderedDict
import inspect

_cache = '.cache'
_install_name = 'penv'
_virtualenv_name = 'virtualenv'
VIRTUALENV_URL = 'https://pypi.python.org/packages/source/v/' \
                  'virtualenv/virtualenv-16.0.0.tar.gz'


def version():
    version = (2, 3, 0, '.dev6')
    v_format = ".".join([str(s) for s in version[:3]])
    if(len(version) > 3):
        v_format += version[3]
    return v_format


def header():
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
    return path.abspath(inspect.getfile(inspect.currentframe()))


def plugin_path():
    current = current_file_path()
    return path.dirname(path.dirname(current))


def plugin_name():
    plugin_path = plugin_path()
    return path.basename(plugin_path)


def packages_path():
    """
    Get sublime text package folder
    """
    deviot_path = plugin_path()
    packages_path = path.dirname(deviot_path)
    return packages_path


def user_plugin_path():
    plugin = packages_path()
    return path.join(plugin, 'User', 'Deviot')


def cache_path():
    deviot = user_plugin_path()
    return path.join(deviot, _cache)


def dependencies_path():
    deviot = user_plugin_path()
    return path.join(deviot, _install_name)


def bin_name():
    bin = 'bin'
    if('windows' in sublime.platform()):
        bin = 'Scripts'
    return bin


def bin_path():
    dependencies = dependencies_path()
    return path.join(dependencies, bin_name())


def pio_penv():
    """
    ~/.platformio/penv/bin
    """
    user_path = path.expanduser('~')
    return path.join(user_path, '.platformio', 'penv', bin_name())


def setting_path():
    """
    Packages/User/Deviot/deviot.ini
    """
    deviot_path = user_plugin_path()
    system_ini_path = path.join(deviot_path, 'deviot.ini')
    return system_ini_path


def virtualenv_path():
    dependencies = dependencies_path()
    return path.join(dependencies, _virtualenv_name)


def user_pio_path():
    """
    Deviot file in Packages/User/Deviot/pio
    """
    user_path = user_plugin_path()
    return path.join(user_path, 'pio')


def boards_file_path():
    """
    Deviot file in Packages/User/Deviot/pio/boards.json
    """
    user_data = user_pio_path()
    return path.join(user_data, 'boards.json')


def virtualenv_list():
    return VIRTUALENV_URL.split('/')


def virtualenv_name():
    url_list = virtualenv_list()
    list_number = len(url_list)
    return url_list[list_number - 1]


def virtualenv_file():
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
    env_paths = get_sysetting('env_paths', False)
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
