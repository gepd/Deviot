import sublime
import sublime_plugin

from os import path
import inspect

_cache = '.cache'
_install_name = 'penv'
_virtualenv_name = 'virtualenv'
_virtualenv_url = 'https://pypi.python.org/packages/source/v/' \
                  'virtualenv/virtualenv-14.0.6.tar.gz'


def version():
    version = (2, 3, 0, '.dev4')
    v_format = ".".join([str(s) for s in version[:3]])
    if(len(version) > 3):
        v_format += version[3]
    return v_format


def header():
    deviot_v = version()
    sublime_v = sublime.version()
    user_agent = 'Deviot/%s (Sublime-Text/%s)' % (deviot_v, sublime_v)
    return {'User-Agent': user_agent}


def current_file_path():
    return path.abspath(inspect.getfile(inspect.currentframe()))


def plugin_path():
    current = current_file_path()
    return path.dirname(current)


def user_plugin_path():
    plugin = plugin_path()
    return path.join(plugin, 'User', 'Deviot')


def cache_path():
    deviot = user_plugin_path()
    return path.join(deviot, _cache)


def dependencies_path():
    deviot = user_plugin_path()
    return path.join(deviot, _install_name)


def bin_path():
    bin = 'bin'
    dependencies = dependencies_path()
    if('windows' in sublime.platform()):
        bin = 'Scripts'
    return path.join(dependencies, bin)


def virtualenv_path():
    dependencies = get_dependencies_path()
    return path.join(dependencies, _virtualenv_name)


def virtualenv_list():
    return _virtualenv_url.split('/')


def virtualenv_file():
    cache = cache_path()
    url_list = virtualenv_list()
    list_number = len(url_list)
    return path.join(cache, url_list[list_number - 1])
