[![https://github.com/gepd/Deviot/blob/master/LICENCE](https://img.shields.io/badge/Licence-%20Apache%20Software%20License-green.svg)](https://github.com/gepd/Deviot/blob/master/LICENCE)
[![https://gratipay.com/~gepd/](https://img.shields.io/donate/Deviot.png?color=yellow)](https://gratipay.com/~gepd/)

English | [Español](https://github.com/gepd/Deviot/blob/master/Docs/README-es.md)

# Deviot
**Deviot** is a plugin based in [stino](https://github.com/Robot-Will/Stino) for Sublime Text 3 to IoT development, it uses [PlatformIO](http://platformio.org/) ecosystem which support more than **~270** boards.

#### - Colored Output Console
More legibility to read error(s) in you code.

![Colored Console](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/colored_console.png?raw=true)

#### - Quick Search
An easy way to search between the list with more than 270 boards

![Quick Search](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/quick_search.png?raw=true)

* [Full board list](http://platformio.org/boards)

#### - Library Search
Easy library manager to search and install or remove your libraries without any effort

![Library Search](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/library_search.png?raw=true)

* [Read about private libraries](https://github.com/gepd/Deviot/blob/master/Docs/Private_Library.md)

#### - Snippets
![Snippets](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/snippets.gif?raw=true)

* [All the snippets availables](https://github.com/gepd/Deviot/blob/master/Docs/snippets.md)

#### - OTA

At this moment OTA is only available in `Espressif` [development platform](http://platformio.org/boards?count=15&filter%5Bplatform%5D=espressif&page=1&sorting%5Bvendor%5D=asc) (ESP8266).

![OTA](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/ota.png?raw=true)

#### - PlatformIO

- If you have used **PlatformIO CLI**, you can compile your sketches as always. 
- If you come from **Arduino/Genuino IDE**, don't worry Deviot will not modify the structure of your files

![Pio](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/platformio_structure.png?raw=true)

# Setup

Remember to choose `Add python.exe to Path` when you install it in Windows.

![Install Python](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/win_python.gif?raw=true)

* 1. [Install Python 2](https://www.python.org/downloads/)
* 2. Using the [package control](https://packagecontrol.io/installation), install the package called `Deviot` from the list.
* 3. Wait until the plugin is completely installed.

![Install Deviot](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/deviot_install_.gif?raw=true)


## - Use the plugin

1. Code your firmware
2. Build or upload your code (You will be prompted to choose your build/upload options)
3. Done!

![Deviot Preview](https://github.com/gepd/Deviot/blob/feature/v1.2.0/Docs/images/deviot1.gif?raw=true)


## - Languages 
Deviot is available in **English**, **Spanish**, **French**, **Korean**(Incomplete), **Chinese**(Incomplete)

If you want to contribute and translate it to your language use [this template](https://github.com/gepd/Deviot/blob/master/Languages/preset.txt) or any other language file as reference. 

You should let the `msgid` as is, and paste your translated string in `msgstr`. When you finish it **pull a request** with the new file. The file should be called in the [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) format (two letters) and with the extension `.lang`

## - Thanks to
* **[PlatformIO](http://www.platformio.org)**: Ivan Kravets
* **Korean Translation:** @gro
* **Chinese Translation:** @chkb123456
* **French Translation:** @Alnoa
* **Code Contributor:** @goolic

## - Donate
Support the open source, if you liked this plugin and you want to make a contribution to continue developing it, do it through [this link](https://gratipay.com/~gepd/). If you have any problem or you want to contact me: <gepd@outlook.com>


##  - Licence
Copyright 2015-2016 GEPD <gepd@outlook.com>

Deviot is licensed with the permissive Apache 2.0 licence. It means that you can use it personal or commercially, free of charge.

[Read](https://github.com/gepd/Deviot/blob/master/LICENCE) the full Licence file.