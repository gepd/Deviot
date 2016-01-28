# Deviot - Beta
![Deviot preview](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot.gif?raw=true)

Sublime Text plugin (for v2&3) for IoT development using [PlatformIO](http://platformio.org/) ecosystem and supporting **~200** boards!

The integration with platformIO is not 100% ready, but will be in the near future. 
If you want to help me, please feel free to do it at any way you can.

---
Plugin para Sublime text (v2&3) que ayuda al desarrollo de aplicaciones IoT usando el ecosistema [platformIO](http://platformio.org/) que soporta ¡más de **~200** placas!

La integración con platformIO no está 100% lista, pero lo estará en un futuro cercano.
Si quieres ayudarme, siéntete libre de hacerlo en la forma que más te acomode.

## Setup / Instalación

![Install Deviot](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot_install.gif?raw=true)

* [Install platformIO](https://github.com/gepd/Deviot/blob/master/Docs/setup.md) (Better if you do it before the plugin)
* Using the [package control](https://packagecontrol.io/installation), add a new repository to Sublime Text
* Install the package `Deviot` from the list
* If you see `Install platformIO` in the main menu, go to `Set environment PATH` and paste the path where python/platformIO was installed

To know detailed information about the setup of platformIO go to [this document](https://github.com/gepd/Deviot/blob/master/Docs/setup.md)

---
* [Instala platformIO](https://github.com/gepd/Deviot/blob/master/Docs/setup.md) (Mejor si lo haces antes que el plugin)
* Utilizando el [control de paquetes](https://packagecontrol.io/installation), agrega un nuevo repositorio a Sublime Text `https://github.com/gepd/Deviot.git`
* Instala el paquete llamado `Deviot` desde la lista
* Si vez `Instala platformIO` en el menú principal, anda a `Ingresar Ruta de Entorno` y pega la ruta donde instalaste python/platformIO

Para conocer información con más detalles de los pasos de instalación de platformIO visíta [este documento](https://github.com/gepd/Deviot/blob/master/Docs/setup.md)

## How to use the plugin / Como usar el plugin
1. Code your firmware
2. From the **Deviot** menu select one or more boards, an environment to work and a COM port
3. Build or upload your code
4. Done!

---
1. Escribe tu código
2. Desde el menú **Deviot** selecciona una o más placas, un entorno de desarrollo, y un puerto COM
3. Compila o carga tu código
4. ¡Hecho!

## Libraries / Librerías

![Install Library](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot_libraries.gif?raw=true)

Deviot is using the platformIO library manager, it organizes multiple libraries in one place, so you will be able to install a library with a few steps.

---
Deviot usa el gestor de librerías de platformIO, este gestor organiza múltiples librerías en un sólo lugar, por lo que te será muy fácil poder instalar una.

#### Install Library / Instalar Librería

- From the top `Deviot` menu go to `Search Library`
- In the input field, writes the keyword to search the library
- When appears the results, choose one library and wait until it's installed
- Now you will be available to use it adding `#include <library_name.h>` at the top of you code

If you need to install a library that isn't in the library manager, follow the next steps:

- From the top Deviot menu go to `Library Options` >> `Open User Libraries Folder`
- Copy your Library in that folder

[**Read more**](https://github.com/gepd/Deviot/blob/master/Docs/Private_Library.md) about how yor private library should be organized

---
- Desde el menu `Deviot` anda a `Buscar Librería`
- En el campo de búsqueda, escribe una palabra clave para buscar la librería.
- Cuando aparezca el resultado, selecciona la librería y espera hasta que sea instalda
- Ahora podrás usarla agregando `#include <nombre_libreria.h>` al comienzo de tu código

Si necesitas instalar una librería que no está en el gestor, sigue los siguientes pasos:

- Desde el menu `Deviot` anda a `Opciones de Librerías` >> `Abrir Carpeta con Librerías de Usuario`
- Copia tu librería en esa carpeta

[**Leer más**](https://github.com/gepd/Deviot/blob/master/Docs/Private_Library.md) sobre cómo tu librería privada debería estar organizada.

## Languages / Idiomas
At this moment **Deviot** is available in english and spanish. If you want to contribute and translate it to your language use [this as template](https://github.com/gepd/Deviot/blob/master/Languages/en.lang) (or any other in that folder). You should let the `msgid` as is, and paste your translated string in `msgstr`. When you finish it [pull a request](https://github.com/gepd/Deviot/pulls) with the new file.

The file should be called in the [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) format (two letters) and with the extension `.lang`

---
En este momento **Deviot** está disponible en inglés y español. Si deseas ayudar y traducir el plugin a tu idioma, usa [este archivo](https://github.com/gepd/Deviot/blob/master/Languages/en.lang) como referencia (o cualquier otro en esa carpeta). Debes dejar la cadena `msgid` como está, y pegar tu palabra/oración en `msgstr`. Cuando finalices, envía el nuevo archivo con un [pull request](https://github.com/gepd/Deviot/pulls)

El archivo debe ser nombrado en el formato [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (dos letras) y con la extensión `.lang`

## To Do / Por hacer
- [x] <del>Add Serial Monitor</del>
- [x] <del>Languages</del>
- [x] <del>PlatformIO API Libraries integration</del>
- [ ] Recognise library examples
- [ ] OTA Serial ports

---
- [x] <del>Agregar Monitor Serial</del>
- [x] <del>Idiomas</del> 
- [x] <del>Intengración de la API para librerías de platformIO</del>
- [ ] Reconocer ejemplos de librerías
- [ ] Puertos Seriales OTA

**This plugin is under development, don't use in a production environment.**

**Este plugin aún está en desarrollo, no usar en un ambiente de producción**
