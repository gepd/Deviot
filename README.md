[![https://github.com/gepd/Deviot/blob/master/LICENCE](https://img.shields.io/badge/Licence-%20Apache%20Software%20License-green.svg)](https://github.com/gepd/Deviot/blob/master/LICENCE)
[![https://gratipay.com/~gepd/](https://img.shields.io/donate/Deviot.png?color=yellow)](https://gratipay.com/~gepd/)

English | [Español](https://github.com/gepd/Deviot/blob/master/Docs/README-es.md)

# Deviot

**Deviot** is a plugin based on [stino](https://github.com/Robot-Will/Stino) for Sublime Text 3. It uses the [PlatformIO](http://platformio.org/) ecosystem, which supports more than **270** boards.



# Features

#### • Colored Output Console

More legibility to read error(s) in your code.

![Colored Console](https://github.com/gepd/Deviot/blob/master/Docs/images/colored_console.png?raw=true)

#### • Quick Search

An easy way to search more than 270 boards

![Quick Search](https://github.com/gepd/Deviot/blob/master/Docs/images/quick_search.png?raw=true)

[Full board list](http://platformio.org/boards)

#### • Library Search

Library manager to search, install or remove your libraries easily

![Library Search](https://github.com/gepd/Deviot/blob/master/Docs/images/library_search.png?raw=true)

[Read about private libraries](https://github.com/gepd/Deviot/blob/master/Docs/Private_Library.md)

#### • Snippets

![Snippets](https://github.com/gepd/Deviot/blob/master/Docs/images/snippets.gif?raw=true)

[All the snippets availables](https://github.com/gepd/Deviot/blob/master/Docs/snippets.md)

#### • OTA

At this moment OTA is only available in `Espressif` [development platform](http://platformio.org/boards?count=15&filter%5Bplatform%5D=espressif&page=1&sorting%5Bvendor%5D=asc) (ESP8266).

![OTA](https://github.com/gepd/Deviot/blob/master/Docs/images/ota.png?raw=true)

#### • PlatformIO

* If you have used **PlatformIO CLI**, you can compile your sketches as always. 
* If you come from **Arduino/Genuino IDE**, don't worry. Deviot will not modify the structure of your files.

![Pio](https://github.com/gepd/Deviot/blob/master/Docs/images/platformio_structure.png?raw=true)



# Setup

*Remember to choose `Add python.exe to Path` when you install python in Windows.*

![Install Python](https://github.com/gepd/Deviot/blob/master/Docs/images/win_python.gif?raw=true)

1. [Install Python 2](https://www.python.org/downloads/)
2. Using [package control](https://packagecontrol.io/installation), search for and install `Deviot` from the list.
3. Wait for the plugin to finish installing



![Install Deviot](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot_install_.gif?raw=true)



# Using the plugin

*The first time you run the program, you will be prompted to select your board*

![Deviot Preview](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot1.gif?raw=true)

1. Write your code
2. Build and upload your code
3. Done!



## Languages

Deviot is available in **English**, **Spanish**, **French** (Incomplete), **Korean** (Incomplete), and ** Chinese**

If you want to contribute and translate it to your language, use [this template](https://github.com/gepd/Deviot/blob/master/Languages/en.lang) or any other language file as reference. ([Languages availables](https://github.com/gepd/Deviot/tree/master/Languages))

You should let the `msgid` as is, and paste your translated string in `msgstr`. When you finish it **pull a request** with the new file. The file should be called in the [ISO 639*1](https://en.wikipedia.org/wiki/List_of_ISO_639*1_codes) format (two letters) and with the extension `.lang`



## Thanks to

* **[PlatformIO](http://www.platformio.org)**: Ivan Kravets
* **Korean Translation:** @gro
* **Chinese Translation:** @chkb123456, loong
* **French Translation:** @Alnoa
* **Code Contributor:** @goolic



## Donate

If you liked this plugin, and you want to make a contribution to continue its development, do it through [this link](https://gratipay.com/~gepd/). If you have any problems, or want to contact me: <gepd@outlook.com>



## License

Copyright 2015-2016 GEPD <gepd@outlook.com>

Deviot is licensed with the permissive Apache 2.0 licence. It means that you can use it personal or commercially, free of charge.

[Read](https://github.com/gepd/Deviot/blob/master/LICENCE) the full Licence file.
