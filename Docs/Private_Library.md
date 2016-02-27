
# Deviot - Libraries
![Private Library](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot_libraries.gif?raw=true)

### How to use

Deviot uses a library manager provided by platformio, you can install or delete a library with a few steps.

##### Install Library
`Deviot Menu > Search Library` <sub>Shortcut (Alt+L, Alt+S)</sub>

##### Remove Library
`Deviot Menu > Remove Library` <sub>Shortcut (Alt+L, Alt+R)</sub>

Every time you install or remove a library, the menu list `Import Library` and `Examples` are automatically updated. When you install a library manually you need to restart Sublime Text

### Install Library Manually

To install a library manually go to: `Deviot Menu > Library Options > Open Library Folder`

This directory is intended for the project specific (private) libraries.
Deviot (platformIO) will compile them to static libraries and link to executable file.

The source code of each library should be placed in separate directory, like
"lib/private_lib/[here are source files]".

For example, see how can be organised `Foo` and `Bar` libraries:

![Private Library](https://github.com/gepd/Deviot/blob/master/Docs/images/private_library.png?raw=true)


Then in `main.c` (or what you are using) you should use:

`#include <Foo.h>`

`#include <Bar.h>`

`rest of H/C/CPP code`

Deviot (platformIO) will find your libraries automatically, configure preprocessor's
include paths and build them.

See additional options for PlatformIO Library Dependency Finder `lib_*`:
http://docs.platformio.org/en/latest/projectconf.html#lib-install