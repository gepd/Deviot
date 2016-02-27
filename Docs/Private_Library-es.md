
# Deviot Librerías
![Private Library](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot_libraries.gif?raw=true)

### Cómo usar

Deviot usa el gestor de librerías de platformio, puedes instalar o liminar librerías con solo algunos pasos.

##### Instalar Librería
`Menu Deviot > Buscar Librería` <sub>Shortcut (Alt+L, Alt+S)</sub>

##### Eliminar Librería
`Menu Deviot > Eliminar Librería` <sub>Shortcut (Alt+L, Alt+R)</sub>

Cada vez que instalas o eliminas una librería, las listas de los menu `Importar Librería` y `Ejemplos` son actualizadas automáticamente. Cuando instalas una librería manualmente, neceistas reiniciar Sublime Text

### Instalar Librería Manualmente

Para instalar una librería manualmente anda a: `Menu Deviot > Opciones de Librería > Abrir Carpeta con Librerías`

Este directorio está destinado para proyectos con librerías específicas (privadas).
PlatformIO compilará las bibliotecas como estáticas y las enlazará a un archivo ejecutable.

El código fuente de cada biblioteca debe ser colocado en una carpeta por separado, "lib/lib_privada/[aquí tu código fuente]"

Por ejemplo, mira como deben ser organizadas las librerías `Foo` y `bar`:


![Private Library](https://github.com/gepd/Deviot/blob/master/Docs/images/private_library.png?raw=true)


En tu archivo `main.c` (o el que estés usando) deberías usar

`#include <Foo.h>`

`#include <Bar.h>`

`El resto del código H/C/CPP aquí`

Deviot (platformIO) encontrará las librerías automáticamente, y las compilará cuando incluyas su ruta.

Para ver información adicional y más opciones del gestor de librerías de PlatformIO visita:
http://docs.platformio.org/en/latest/projectconf.html#lib-install
