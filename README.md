# Deviot
Sublime Text plugin for IoT development using [PlatformIO](http://platformio.org/) ecosystem and supporting **~200** boards!

The integration with PlatformIO is not 100% ready, but will be in the near future. 
If you want to help me, please feel free to do it at any way you can.

## Setup

* [Install PlatformIO](http://platformio.org/#!/get-started)
* Add a new repository to Sublime Text `https://github.com/gepd/Deviot.git`
* Install the package `Deviot` from the list
* Set the `Sublime Text Menu: Deviot > Set Environment PATH > env_path` setting with the result of `echo $PATH` (Unix) / `echo %PATH%` (Windows).

## How to use
1. Code your firmware
2. From the **Deviot** menu select one or more boards, an environment to work and a COM port
3. Build your code
4. Upload your code
5. Done!

**This plugin is under development, don't use in a production environment.**
