from sublime_plugin import WindowCommand
from ..platformio.project_recognition import ProjectRecognition
from ..libraries.project_check import ProjectCheck

class DeviotOpenIniFile(WindowCommand):
    def run(self):
        views = []

        ini_file = ProjectRecognition().get_ini_path()
        view = self.window.open_file(ini_file)
        views.append(view)

        if(views):
            self.window.focus_view(views[0])

    def is_enabled(self):
        from ..libraries.project_check import ProjectCheck
        
        prj = ProjectCheck()
        iot = prj.is_iot()
        ini = prj.is_initialized()

        if(iot and ini):
            return True
        return False