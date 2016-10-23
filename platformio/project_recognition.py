# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sublime

from ..libraries import tools, paths


class ProjectRecognition(object):

    def __init__(self):
        self.window = sublime.active_window()
        self.view = self.window.active_view()

    def check_project(self):
        """
        check requirements before process a project/file
        """
        if(not self.get_project_path() and 'monitor' in self.get_view_name()):
            return 112

        if(self.is_unsaved() and self.get_project_path() is not None):
            self.save_changes()

        if(self.is_empty()):
            return 113

        if(not self.is_iot() and self.get_project_path()):
            return 114

        if(not self.get_project_path()):
            self.save_file()

        return 200

    def get_project_file_name(self, ext=True):
        """
        Gets the name of the current file
        """

        file_path = self.get_project_path()

        # file name with ext
        file_name = os.path.basename(file_path)

        # file name without ext
        if(not ext):
            file_name = os.path.splitext(file_name)[0]

        return file_name

    def get_file_name(self, ext=True):
        """
        return the file name of the current file
        ext: when is False remove the extension of the file
        True as default
        """

        path = self.get_project_path()

        # file name with extension
        file_name = os.path.basename(path)

        # remove extension
        if(not ext):
            file_name = os.path.splitext(file_name)[0]

        return file_name

    def get_view_name(self):
        """
        return the name of a view if it was assigned
        if wasn't the value is None
        """
        return self.view.name().lower()

    def get_project_path(self):
        """
        return the path of the current project
        (including the file name)
        """
        return self.view.file_name()

    def get_project_folder(self):
        """
        return the folder of the current project
        (without file name)
        """
        file_path = self.get_project_path()
        folder_path = os.path.dirname(file_path)

        return folder_path

    def get_parent_project_path(self):
        """
        return the parent path of the current project
        (including the file name)
        """
        file_path = self.get_project_path()

        folder_path = os.path.dirname(file_path)
        parent = os.path.dirname(folder_path)

        return parent

    def get_working_path(self):
        """
        get the working path based in the type of structure
        platformio or arduino type
        """
        file_path = self.get_project_folder()
        parent_path = self.get_parent_project_path()
        has_init_file = self.has_init_file(parent_path)

        if(has_init_file or file_path.endswith('src')):
            return_path = parent_path
        else:
            temp_name = self.get_project_file_name()
            return_path = self.get_build_path()

            native = tools.get_config('native', True)

            if(native):
                return_path = file_path

        return return_path

    def is_iot(self):
        """
        Check if the file in the current view is an IoT file,
        the type of files are specified in the var exts.
        """
        exts = ['ino', 'pde', 'cpp', 'c', '.S']
        path = self.get_project_path()

        if path and path.split('.')[-1] in exts:
            return True
        return False

    def is_native(self):
        """
        checks if the current project is native type or not
        based in the location of the file platformio.ini
        """
        native = False
        file_path = self.get_project_path()
        force_native = tools.get_config('force_native', False)

        # only if file has been saved
        if(file_path):
            parent_path = self.get_parent_project_path()

            # find platformio.ini
            for file in os.listdir(parent_path):
                if(file.endswith('platformio.ini')):
                    tools.save_config('native', True)
                    return True

        # check if horce native was selected
        if(force_native):
            native = True

        # if is stored in the temp folder set as native
        if(not force_native):
            if("Temp" in file_path or "tmp" in file_path):
                native = True

        # save in preferences file
        tools.save_config('native', native)

        return native

    def is_unsaved(self):
        """
        return True if the view has unsaved changes
        """
        return self.view.is_dirty()

    def save_changes():
        """
        Save changes in a file already saved
        """
        self.view.run_command('save')

    def is_empty(self):
        """
        return True if the view is empty
        """
        size = self.get_project_size()

        if(size > 0):
            return False
        return True

    def get_project_size(self):
        """
        return the size of the current sketch
        """
        return self.view.size()

    def get_build_path(self):
        """
        get default build path or custom path selected
        by the user
        """
        file_name = self.get_project_file_name(ext=False)
        build_dir = tools.get_setting('build_dir', False)

        if(build_dir):
            build_dir = os.path.join(build_dir, file_name)
            return build_dir
        return paths.getTempPath(file_name)

    def get_ini_path(self):
        """
        get the path of the platformio.ini file
        """
        project_folder = self.get_working_path()
        ini_path = os.path.join(project_folder, 'platformio.ini')

        return ini_path

    def has_init_file(self, path):
        """
        Check if platformio.ini exist in the given path
        """
        if(os.path.isdir(path)):
            for file in os.listdir(path):
                if(file.endswith('platformio.ini')):
                    return True
        return False

    def get_envs_initialized(self):
        """
        this function return a list with all the
        available environments in the platformio.ini file
        """
        ini_path = self.get_ini_path()
        environments = []

        if(os.path.exists(ini_path)):
            from ..libraries.configobj.configobj import ConfigObj

            ini_file = ConfigObj(ini_path)

            for pio_env in ini_file:
                if('env:' in pio_env):
                    environments.append(pio_env.split(":")[1])

        return environments

    def get_envs(self):
        """
        get the environments pre selected and saved in the config
        file
        """
        envs = []
        file_name = self.get_file_name(ext=False)
        envs_initialized = self.get_envs_initialized()
        envs.extend(envs_initialized)

        envs_selected = tools.get_config('environments')

        if(envs_selected and file_name in envs_selected):
            envs.extend(envs_selected[file_name])
            envs = list(set(envs))

        return envs

    def check_env_in_file(self):
        """
        check if the selected environment is initialized or not
        """
        env_selected = tools.get_config('environment_selected')
        env_selected = self.get_project_file_name(ext=False)

        env_list = self.get_envs_initialized()

        if(env_selected in env_list):
            return 200
        return 115

    def save_file(self):
        """
        If the sketch in the current view has been not saved, it generate
        a random name and stores in a temp folder.
        """
        import time
        from ..libraries.file import File

        ext = '.ino'

        file_name = str(time.time()).split('.')[0]
        temp_path = paths.getTempPath()
        file_path = os.path.join(temp_path, file_name, 'src')
        full_path = file_name + ext
        full_path = os.path.join(file_path, full_path)

        tools.make_folder(file_path)

        region = sublime.Region(0, self.view.size())
        text = self.view.substr(region)

        file = File(full_path)
        file.write(text)

        self.view.set_scratch(True)
        self.window.run_command('close')
        self.view = self.window.open_file(full_path)
