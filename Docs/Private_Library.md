
#Deviot - Libraries / Librerías

###User_Libs

This directory is intended for the project specific (private) libraries.
Deviot (platformIO) will compile them to static libraries and link to executable file.

The source code of each library should be placed in separate directory, like
"User_Libs/private_lib/[here are source files]".

For example, see how can be organised `Foo` and `Bar` libraries:

![Private Library](https://github.com/gepd/Deviot/blob/master/Docs/images/private_library.png?raw=true)


Then in `src/main.c` (or what you are using) you should use:

`#include <Foo.h>`

`#include <Bar.h>`

`rest of H/C/CPP code`

Deviot (platformIO) will find your libraries automatically, configure preprocessor's
include paths and build them.

See additional options for PlatformIO Library Dependency Finder `lib_*`:
http://docs.platformio.org/en/latest/projectconf.html#lib-install

---
###User_Libs

Este directorio está destinado para proyectos con librerías específicas (privadas).
PlatformIO compilará las bibliotecas como estáticas y las enlazará a un archivo ejecutable.

El código fuente de cada biblioteca debe ser colocado en una carpeta por separado, "User_Libs/lib_privada/[aquí tu código fuente]"

Por ejemplo, mira como deben ser organizadas las librerías `Foo` y `bar`:


![Private Library](https://github.com/gepd/Deviot/blob/master/Docs/images/private_library.png?raw=true)


En tu archivo `main.c` (o el que estés usando) deberías usar

`#include <Foo.h>`

`#include <Bar.h>`

`El resto del código H/C/CPP aquí`

Deviot (platformIO) encontrará las librerías automáticamente, y las compilará cuando incluyas su ruta.

Para ver información adicional y más opciones del gestor de librerías de PlatformIO visita:
http://docs.platformio.org/en/latest/projectconf.html#lib-install
