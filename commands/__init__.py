from .deviot_new_sketch import DeviotNewSketchCommand
from .deviot_select_boards import DeviotSelectBoardsCommand
from .deviot_select_environment import DeviotSelectEnvironmentCommand
from .deviot_search_library import DeviotSearchLibraryCommand
from .deviot_update_library import DeviotUpdateLibraryCommand
from .deviot_remove_library import DeviotRemoveLibraryCommand
from .deviot_import_library import DeviotImportLibraryCommand
from .deviot_insert_library import DeviotInsertLibraryCommand
from .deviot_libraries_examples import DeviotLibraryExamplesCommand
from .deviot_open_library_folder import DeviotOpenLibraryFolderCommand
from .deviot_rebuild_lib_list import DeviotRebuildLibListCommand
from .deviot_extra_library_folder import DeviotExtraLibraryFolderCommand
from .deviot_remove_extra_library_folder import DeviotRemoveExtraLibraryFolderCommand
from .deviot_compile_sketch import DeviotCompileSketchCommand
from .deviot_upload_sketch import DeviotUploadSketchCommand
from .deviot_overwrite_upload_baud import DeviotOverwriteUploadBaudCommand
from .deviot_clean_sketch import DeviotCleanSketchCommand
from .deviot_freeze_sketch import DeviotFreezeSketchCommand
from .deviot_pio_untouch import DeviotPioUntouchCommand
from .deviot_open_ini_file import DeviotOpenIniFile
from .deviot_show_console import DeviotShowConsoleCommand
from .deviot_hide_console import DeviotHideConsoleCommand
from .deviot_choose_programmer import DeviotChooseProgrammerCommand
from .deviot_show_terminal import DeviotShowTerminalCommand
from .deviot_hide_terminal import DeviotHideTerminalCommand
from .deviot_select_port import DeviotSelectPortCommand
from .deviot_set_password import DeviotSetPasswordCommand
from .deviot_toggle_serial_monitor import DeviotToggleSerialMonitorCommand
from .deviot_send_serial_monitor import DeviotSendSerialMonitorCommand
from .deviot_output_console import DeviotOutputConsoleCommand
from .deviot_send_persistent import DeviotSendPersistentCommand
from .deviot_automatic_scroll import DeviotAutomaticScrollCommand
from .deviot_auto_clean import DeviotAutoCleanCommand
from .deviot_choose_baudrate import DeviotChooseBaudrateCommand
from .deviot_choose_line_ending import DeviotChooseLineEndingCommand
from .deviot_choose_display_mode import DeviotChooseDisplayModeCommand
from .deviot_upgrade_pio import DeviotUpgradePioCommand
from .deviot_developer_pio import DeviotDeveloperPio
from .deviot_pio_structure import DeviotPioStructureCommand
from .deviot_rebuild_boards import DeviotRebuildBoardsCommand
from .deviot_verbose_output import DeviotVerboseOutputCommand
from .deviot_status_information import DeviotStatusInformationCommand
from .deviot_open_build_folder import DeviotOpenBuildFolderCommand
from .deviot_change_build_folder import DeviotChangeBuildFolderCommand
from .deviot_cpp_file import DeviotCppFileCommand
from .deviot_rebuild_syntax import DeviotRebuildSyntaxCommand
from .deviot_remove_settings import DeviotRemoveSettingsCommand
from .deviot_languages import DeviotLanguagesCommand
from .deviot_donate import DeviotDonateCommand
from .deviot_about import DeviotAboutCommand
from .deviot_pio_about import DeviotPioAboutCommand
from .deviot_clean_view import DeviotCleanViewCommand
from .deviot_clean_console import DeviotCleanConsoleCommand
from .deviot_reload import DeviotReloadCommand
from .deviot_set_ip import DeviotSetIpCommand
from .deviot_history import InputTextHistoryCommand

__all__ = [
    'DeviotNewSketchCommand',
    'DeviotSelectBoardsCommand',
    'DeviotSelectEnvironmentCommand',
    'DeviotSearchLibraryCommand',
    'DeviotUpdateLibraryCommand',
    'DeviotRemoveLibraryCommand',
    'DeviotImportLibraryCommand',
    'DeviotInsertLibraryCommand',
    'DeviotLibraryExamplesCommand',
    'DeviotOpenLibraryFolderCommand',
    'DeviotRebuildLibListCommand',
    'DeviotExtraLibraryFolderCommand',
    'DeviotRemoveExtraLibraryFolderCommand',
    'DeviotCompileSketchCommand',
    'DeviotUploadSketchCommand',
    'DeviotOverwriteUploadBaudCommand',
    'DeviotCleanSketchCommand',
    'DeviotFreezeSketchCommand',
    'DeviotPioUntouchCommand',
    'DeviotOpenIniFile',
    'DeviotShowConsoleCommand',
    'DeviotHideConsoleCommand',
    'DeviotChooseProgrammerCommand',
    'DeviotShowTerminalCommand',
    'DeviotHideTerminalCommand',
    'DeviotSelectPortCommand',
    'DeviotSetPasswordCommand',
    'DeviotToggleSerialMonitorCommand',
    'DeviotSendSerialMonitorCommand',
    'DeviotSendPersistentCommand',
    'DeviotOutputConsoleCommand',
    'DeviotStatusInformationCommand',
    'DeviotAutomaticScrollCommand',
    'DeviotAutoCleanCommand',
    'DeviotChooseBaudrateCommand',
    'DeviotChooseLineEndingCommand',
    'DeviotChooseDisplayModeCommand',
    'DeviotUpgradePioCommand',
    'DeviotDeveloperPio',
    'DeviotPioStructureCommand',
    'DeviotRebuildBoardsCommand',
    'DeviotVerboseOutputCommand',
    'DeviotOpenBuildFolderCommand',
    'DeviotChangeBuildFolderCommand',
    'DeviotCppFileCommand',
    'DeviotRebuildSyntaxCommand',
    'DeviotRemoveSettingsCommand',
    'DeviotLanguagesCommand',
    'DeviotDonateCommand',
    'DeviotAboutCommand',
    'DeviotPioAboutCommand',
    'DeviotCleanViewCommand',
    'DeviotCleanConsoleCommand',
    'DeviotReloadCommand',
    'DeviotSetIpCommand',
    'InputTextHistoryCommand'
]
