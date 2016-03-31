# Deviot Release Notes
### Version 1.1.6 | 31 Mar 2016
* Added compatibility to old libraries (PR https://github.com/gepd/Deviot/pull/11)
* Added feedback while board list are updating
* Avoids show false success messages in user console when the serial port is not selected.
* Fixed issue selecting serial port (https://github.com/gepd/Deviot/issues/12)
* Fixed error showing "New Line" item in Monitor Serial menu

### Version 1.1.5 | 26 Mar 2016
* Fixed update PlatformIO option (Deviot > Options > Upgrade PlatformIO)
* Fixed language strings when python is not installed
* Changed shorcuts icons in Windows 7

### Version 1.1.4 | 21 Mar 2016
* Fixed error installing Pio in ST2 | issue #6
* Minor changes in the about platformio links
* Minor fix using pio in OSX

### Version 1.1.3 | 13 Mar 2016
* Fixed error auto-installing platformio in OSX
* Removed Shortcut icons from OSX
* Others minor bugs fixed

### Version 1.1.2 | 28 Feb 2016
* New option menu "New Sketch"
* New option menu "Use CPP File on New File"
* Bug fix false warning at uploading a firmware
* Minor language string fix

### Version 1.1.0 | 25 Feb 2016
* New Auto-install platformio
* New icon shortcuts (Windows, OSX Only)
* New menu option "Show Build Folder"
* New menu option "Change Build Folder"
* New menu option "Remove Prefences Files"
* New menu option "Donate"
* New menu option "About Platformio"
* New menu option "Upgrade Platformio"
* Reorganized menu "options"
* Bug fixes showing messages in the user console
* Bug fix to avoid display empty examples folder in the library menu
* Bug fix when installing a library manually and it not being recognized
* Bug fix to show selected environments when a sketch hasn't a platformio.ini file
* Others minor bugs fixed

### Version 1.0.0 | 04 Feb 2016
* New import library menu option
* New library examples menu option
* New Option to hide the build/upload/clean status console
* New syntax recognition
* New completions based in the library files (ctrl+space)
* New Add IP manually to work with OTA boards
* New the selected COM port and environment is displayed in the status bar
* Bug fix initializing a board from the menu option
* Others minor bugs fixed

### Version 0.4.2 BETA | 28 Jan 2016
* New display mode Hex + Ascii in monitor serial
* New auto-run monitor serial if before to upload a sketch it was running
* Updated the translation files to simplify the way to internationalize the plugin
* Monitor serial: Removing CR and NULL tag in text mode
* Bug fix trying to upload a sketch with a serial port that was online before.
* Multiples minor bugs fixed

### Version 0.4.1.1 BETA | 27 Jan 2016
* Fixed problem showing errors after compile

### Version 0.4.1 BETA | 27 Jan 2016
* New show compile result in the status bar
* Bug fix in auto-saving file/sketch
* Bug fixes in environment menu after auto-save a file
* Bug fix uploading a sketch when a serial monitor is in use
* Fixed problem showing errors without verbose mode active
* Minor bug fix in send persistent function
* Bug fixes in ST2 to add compability to the plugin
* Fixed multiples minor bugs


### Version 0.4 BETA | 24 Jan 2016
* New Monitor serial
* New option to show the user library folder
* New option to change the user library folder
* Fixed bug showing errors in serial console
* Fixed bug showing library manager in ST2

### Version 0.3 BETA | 19 Jan 2016
* New library manager based on the platformIO API and CLI
* New option to keep temp files
* New recognition of platformio.ini file in Deviot menu
* Fixed shortcuts in Linux
* Fixed bugs in Sublime Text 2
* Fixed order bug in env_var at setup
* Fixed multiples minor bugs

### Version 0.2 BETA | 08 Jan 2016
* Added Multi project recognition (platformIO, Arduino style)
* Added Language(s)
* Improved path environment configuration
* Improved order in plugin files
* Minor bug fixed in ST2

### Version 0.1 BETA | 27 Dec 2015
* New instructions when platformio isn't installed
* New Option to set the environment path
* New port serial handled with pyserial
* New download boards list from platformio API
* New user console
* New basic arduino sintax
* New *verbose output* in "options" menu
* New automatically saved the sketch when build/upload
* Fixed multiples minor bugs

### Version 0.0.1 | 11 Dec 2015
* First alpha release
