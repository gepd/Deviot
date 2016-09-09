# Deviot Release Notes
## Version 1.2.5 | 09 Sep
* Fix persisting bug in mDNSCheck (Issue: https://github.com/gepd/Deviot/issues/59)
* Bug fix to avoid remove 'upload_speed' when it was set manually in the ini file (Issue: https://github.com/gepd/Deviot/issues/58)
* Bug fix checking PlatformIO updates

## Version 1.2.4 | 01 Sep
* New feature to highlight errors in sketch
* New feature to scroll to the error line from console
* Add syntax recognition for boolean, byte and word var type
* Bug Fix checking ota in esp  (issues: https://github.com/gepd/Deviot/issues/53 https://github.com/gepd/Deviot/issues/55)
* Bug fix reading comments in ini file with ";" marker

## Version 1.2.3 | 25 Aug
* New option "Previous" to back when a library was selected in the examples list
* Deviot install uses "virtualenv 14.0.6" to simplify the process
* Improved chinese translation (Thanks to "loong")
* The programmer will be add in the platformio.ini file after selecting it in the menu
* Avoid to check PlatformIO updates when developer version is installed
* Show "Framewor(s)" type in library results
* Show IP of mDNS service in list of ports
* Reload main menu when it's corrupted after an update (Issue: https://github.com/gepd/Deviot/issues/54)
* OTA upload uses the device IP insted of the service name to avoid DNS errors
* Show percentage in console when upload by OTA
* Multiples bug fixes with authentication in OTA uploads
* Bug fix to prevent an error when a sketch folder has been renamed in a non native project
* Bug fix when PlatformIO board list have format problems
* Bug Fix for run monitor serial when none port is selected (issue: https://github.com/gepd/Deviot/issues/52)
* Bug Fix showing message 'Not Found' when the results only have installed libraries
* Bug fix saving the sketch before build/upload
* Bug fix in menu option 'Open Build Config File' introduced in previous release
* Factorized serial port feature
* Factorized project recognition

## Version 1.2.2 | 18 Aug
* Support for PlatformIO 3.0
* Other minor fixes

## Version 1.2.1 | 18 Aug
* Adding console feedback when a PlatformIO update is available

## Version 1.2.0 | 17 Aug
* Support for mDNS autodiscover and upload with mDNS port (OTA)
* New Programmer menu option
* New colors in Deviot Console
* New checks for pio updates automatically and warns to the user
* New `Select Board`, `Select Environment`, `Serial Port`, `Import Library` and `Examples` menu options are shown with quick panel instead of menu list
* New Asks for board, environment or serial port instead of show an error
* New context menu options (shortcuts)
* New Deviot parle Français
* New Deviot 說中國
* New menu option to install platformio 'develop' branch (Deviot Menu > Options > Use Develop...)
* New menu option to use always PlatformIO structure (Deviot Menu > Options > Use PlatformIO Structure)
* New menu option to re-open deviot console (Deviot Menu > Show Deviot Console) (issue https://github.com/gepd/Deviot/issues/44)
* New menu option to display the Serial Monitor in console (Deviot Menu > Monitor Serial > Output in Deviot Console) (Issue https://github.com/gepd/Deviot/issues/32)
* New Ask to restart Sublime Text after change the language
* New Always scrolls to the last line text in Deviot console
* Set the same environment as the last chosen board
* Shows s a warn when the libraries and examples menu are empty
* Shows attempts of error in deviot console when programmer not respond
* Improved status bar information
* Improved plugin time load 
* Fixed minor bugs updating the status bar information after upgrade the plugin or pio
* Fixed auto scroll feature (issue https://github.com/gepd/Deviot/issues/43)
* Fixed issue not showing the right error in not verbose mode (issue https://github.com/gepd/Deviot/issues/39)
* Removed Toolbar
* Removed Support for ST2
* Others minor bugs fixed

## Version 1.1.10 | 28 Jun
* Fix bug saving the platformio version after update it

## Version 1.1.9 | 12 May
* Fixed bug checking the current version of python
* Removed not used context menu options

## Version 1.1.8 | 12 May
* New Snippets
* New Korean Language (Thanks to gro)
* New auto scroll option in deviot menu
* New support to comment and uncomment option (https://github.com/gepd/Deviot/issues/25)
* New Serial Option "Not used" to avoid the error "None serial port selected" when a serial port is not necessary (https://github.com/gepd/Deviot/issues/29)
* New option to save the last path when the file chooser is used
* New option to open the ini config file (related https://github.com/gepd/Deviot/issues/26)
* New options to set and remove default path when the file chooser is used (https://github.com/gepd/Deviot/issues/19)
* Changed "Keep temp files" option selected as default
* Fixed bug not showing an error when Python3 is installed (https://github.com/gepd/Deviot/issues/27)
Fixed "Change build folder" bug (https://github.com/gepd/Deviot/issues/22)

### Version 1.1.7 | 04 Apr 2016
* New option to automatically scroll the monitor serial view to the last received message
* Added missing templates to create a new sketch
* Fixed bug showing the default language when the machine run with an unsupported language (https://github.com/gepd/Deviot/issues/8)
* Fixed feedback messages after install Deviot
* Fix bug showing the environment menu list in Linux Mint (https://github.com/gepd/Deviot/issues/16)

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
