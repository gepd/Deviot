[![https://github.com/gepd/Deviot/blob/master/LICENCE](https://img.shields.io/badge/Licence-%20Apache%20Software%20License-green.svg)](https://github.com/gepd/Deviot/blob/master/LICENCE)
[![https://gratipay.com/~gepd/](https://img.shields.io/donate/Deviot.png?color=yellow)](https://gratipay.com/~gepd/)

English | [Español](https://github.com/gepd/Deviot/blob/master/Docs/README-es.md)

# Deviot
**Deviot** is a plugin based in [stino](https://github.com/Robot-Will/Stino) for Sublime Text 2 & 3 to IoT development using [PlatformIO](http://platformio.org/) ecosystem and supporting **~200** boards!

## Setup

![Install Deviot](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot_install.gif?raw=true)

* [Install Python 2](https://www.python.org/downloads/)
* Using the [package control](https://packagecontrol.io/installation), install the package called `Deviot` from the list.
* Wait until the plugin is completely installed.


## How to use the plugin
![Deviot preview](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot.gif?raw=true)

1. Code your firmware
2. From the **Deviot** menu select one or more boards, an environment to work and a COM port
3. Build or upload your code
4. Done!


##### Other Features
* [Libraries](https://github.com/gepd/Deviot/blob/master/Docs/Private_Library.md)

##### Snippets
| Trigger | Function |
|---------|----------|
|abs| abs()|
|analogRead|analogRead()|
|analogWrite|analogWrite()|
|attachInterrupt|attachInterrupt()|

[See the full table with all the snippets availables](https://github.com/gepd/Deviot/blob/master/Docs/snippets.md)

## Languages 
At this moment **Deviot** is available in english and spanish. If you want to contribute and translate it to your language use [this template](https://github.com/gepd/Deviot/blob/master/Languages/preset.txt) and any other language file as reference. 

You should let the `msgid` as is, and paste your translated string in `msgstr`. When you finish it **pull a request** with the new file.

The file should be called in the [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) format (two letters) and with the extension `.lang`


## Donate
Support the open source, if you liked this plugin and you want to make a contribution to continue with the developing it, do it through [this link](https://gratipay.com/~gepd/)

If you have any problem or you want to contact me: <gepd@outlook.com>


## Licence
Copyright 2015-2016 GEPD <gepd@outlook.com>

Deviot is licensed with the permissive Apache 2.0 licence. It means that you can use it personal or commercially, free of charge.

[Read](https://github.com/gepd/Deviot/blob/master/LICENCE) the full Licence file.