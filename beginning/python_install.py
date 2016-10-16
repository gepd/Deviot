from re import sub

from ..libraries import tools


def check_python():
    """
    check if python 2 is installed
    """
    settings = sublime.load_settings("Deviot.sublime-settings")
    pylink = settings.get('pylink', 'python')

    # checking python
    cmd = [pylink, '--version']
    out = tools.run_command(cmd)

    error_code = out[0]
    version = sub(r'\D', '', out[1])

    if(error_code):
        return 100

    if(int(version[0]) > 2):
        return {101: "not python 2"}

    return 200
