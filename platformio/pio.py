from sys import exit

from ..api import deviot
from .command import Command
from ..libraries.messages import Messages
from ..libraries.project_check import ProjectCheck
from ..libraries.tools import save_setting, save_sysetting, get_setting

logger = deviot.create_logger('Deviot')


class Pio(ProjectCheck):
    def __init__(self, cmd):
        super(Pio, self).__init__()

        # set console ouput
        messages = Messages()
        messages.initial_text('_deviot_starting{0}', deviot.version())
        messages.create_panel()

        cmd.init(messages=messages)

        # Class to run the commands
        self.command = cmd.run
        self.print = messages.print

    def initialize(self):
        """
        Runs the init command to start working with a new board
        Initialize a new folder you need to know the board id
        and pass it as an argument in the class

        Initialize(board_id)

        The code will run in a new thread to avoid block the
        execution of the sublime text while platformio is working
        """

        if(not self.check_main_requirements()):
            return

        logger.debug("==============")
        logger.debug("initialize")

        self.check_board_selected()
        if(not self.board_id):
            return

        envs = self.get_envs_initialized()
        if(envs and self.board_id in envs):
            return True

        cmd = ['init', '-b ', self.board_id]
        self.command(cmd, cwd=self.cwd)

        self.structurize_project()

    def compile(self):
        """Compilation

        Starts the compilation command, it first checks if the file in the
        current view is a .iot file and if a board (environment) has been
        selected
        """

        self.initialize()

        save_sysetting('last_action', self.COMPILE)

        if(not self.board_id):
            self.print("select_board_list")
            return

        self.add_option('lib_extra_dirs')

        # check if there is a new speed to overwrite
        self.add_option('upload_speed')

        # add src_dir option if it's neccesary
        self.override_src()

        cmd = ['run', '-e ', self.board_id]
        self.command(cmd, cwd=self.cwd)

        self.after_complete()

    def upload(self):
        """Upload

        Run the upload platformio command checking if a board (environment)
        and a serial port is selected
        """

        # check board selected or make select it
        self.check_board_selected()

        save_sysetting('last_action', self.UPLOAD)

        if(not self.board_id):
            self.print("select_board_list")
            return

        # check port selected or make select it
        self.check_port_selected()
        if(not self.port_id):
            self.print("select_port_list")
            return

        port_id = self.port_id

        # initialize board if it's not
        self.initialize()

        # add extra library board
        self.add_option('lib_extra_dirs', append=True)

        # check if there is a new speed to overwrite
        self.add_option('upload_speed')

        # loads data from platformio.ini
        self.read_pio_preferences()

        # check if there is a programmer selected
        self.programmer()

        programmer = get_setting('programmer_id', None)
        if(programmer):
            cmd = ['run', '-t', 'program', '-e', self.board_id]
        else:
            cmd = ['run', '-t', 'upload', '-e', self.board_id]
            if(port_id != 'not'):
                cmd.extend(['--upload-port', port_id])

        if(not self.check_auth_ota()):
            self.print("ota_error_platform")
            save_sysetting('last_action', None)
            return

        self.check_serial_monitor()

        # add src_dir flag if it's neccesary
        self.override_src()

        self.command(cmd, cwd=self.cwd)

        self.after_complete()

        if(get_setting('run_monitor', None)):
            from ..libraries.serial import toggle_serial_monitor
            toggle_serial_monitor(port_id)
        save_setting('run_monitor', None)

    def clean(self):
        """Cleaning

        Starts the cleaning command. This command cleand the binary files
        in the .pioenvs folder (hidden in unix system)
        """
        if(not self.check_main_requirements()):
            return

        self.check_board_selected()
        if(not self.board_id):
            return

        envs = self.get_envs_initialized()
        if(envs and self.board_id not in envs):
            self.derror("init_not_possible")
            return

        cmd = ['run', '-t', 'clean', '-e ', self.board_id]
        self.command(cmd, cwd=self.cwd)

    def after_complete(self):
        """At complete

        This method will run functions after complete a compilation
        or upload an sketch. You should only put here a fuction or
        a method
        """
        pio_untouch = get_setting('pio_untouch', False)
        if(pio_untouch):
            # remove lib_extra_dirs option
            self.add_option('lib_extra_dirs', wipe=True)

            # remove programmer flags
            self.programmer(wipe=True)

            # remove upload_speed
            self.add_option('upload_speed', wipe=True)

        # none last action
        save_sysetting('last_action', None)
