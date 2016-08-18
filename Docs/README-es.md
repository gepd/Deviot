[![https://github.com/gepd/Deviot/blob/master/LICENCE](https://img.shields.io/badge/Licence-%20Apache%20Software%20License-green.svg)](https://github.com/gepd/Deviot/blob/master/LICENCE)
[![https://gratipay.com/~gepd/](https://img.shields.io/donate/Deviot.png?color=yellow)](https://gratipay.com/~gepd/)

[Inglés](https://github.com/gepd/Deviot/blob/master/README.md) | Español

# Deviot
**Deviot** es un plugin basado en [stino](https://github.com/Robot-Will/Stino) para Sublime Text 3 en el que puedes desarrollar aplicacion para dispositivos IoT, usa el ecosistema [PlatformIO](http://platformio.org/) que soporta ¡más de **~270** placas!

#### - Consola de Salida Coloreada
Más legibilidad para leer los errores en tu código

![Consola Coloreada](https://github.com/gepd/Deviot/blob/master/Docs/images/colored_console.png?raw=true)

#### - Quick Search
Una forma rápida para buscar entre la lista de más de 270 tarjetas de desarollos.

![Quick Search](https://github.com/gepd/Deviot/blob/master/Docs/images/quick_search.png?raw=true)

* [Lis completa de placas](http://platformio.org/boards)

#### - Gestor de Librerías
Busca, Instala o elimina fácilmente cualquier librería que necesites para tu proyecto

![Gestor de Librerias](https://github.com/gepd/Deviot/blob/master/Docs/images/library_search.png?raw=true)

* [Leer sobre la instalación de librerías privadas](https://github.com/gepd/Deviot/blob/master/Docs/Private_Library.md)

#### - Snippets
![Snippets](https://github.com/gepd/Deviot/blob/master/Docs/images/snippets.gif?raw=true)

* [Todos los snippets disponibles](https://github.com/gepd/Deviot/blob/master/Docs/snippets.md)

#### - OTA
En este momento OTA (over-the-air) está disponible solo en las [plataformas de desarrollo](http://platformio.org/boards?count=15&filter%5Bplatform%5D=espressif&page=1&sorting%5Bvendor%5D=asc) `Espressif` (ESP8266)

![OTA](https://github.com/gepd/Deviot/blob/master/Docs/images/ota.png?raw=true)

#### - PlatformIO
- Si has usas **PlatformIO CLI** puedes compilar/usar tus sketches como siempre.
- Si vienes desde el **IDE de Arduino/Genuino**, no te preocupes, Deviot no modificará la estructura de tus archivos.

![Pio](https://github.com/gepd/Deviot/blob/master/Docs/images/platformio_structure.png?raw=true)

# Instalación

Recuerda seleccionar `Add python.exe to Path` cuando instales python en Windows.

![Instalar Python](https://github.com/gepd/Deviot/blob/master/Docs/images/win_python.gif?raw=true)

* 1. [Instalar Python 2](https://www.python.org/downloads/)
* 2. Usando [package control](https://packagecontrol.io/installation), instala el paquete llamado `Deviot` desde la lista.
* 3. Espera hasta que el plugin esté completamente instalado.

![Instalar Deviot](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot_install_.gif?raw=true)


## - Usar el plugin

1. Escribe tu código
2. Compila o sube tu código (Tendrás que seleccionar tus preferencias de compilación/subida)
3. ¡Listo!

![Deviot Preview](https://github.com/gepd/Deviot/blob/master/Docs/images/deviot1.gif?raw=true)


## - Idiomas
Deviot está disponible en **Inglés**, **Español**, **Francés**, **Koreano**(Incompleto), **Chino**(Incompleto)

 Si deseas ayudar y traducir el plugin a tu idioma, usa [esta pantilla](https://github.com/gepd/Deviot/blob/master/Languages/es.lang) y cualquier otro archivo de idioma como referencia. ([Idiomas disponibles](https://github.com/gepd/Deviot/tree/master/Languages))

Debes dejar la cadena `msgid` como está, y pegar tu palabra/oración traducido/a en `msgstr`. Cuando finalices, envía el nuevo archivo con un **pull request**. El archivo debe ser nombrado en el formato [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (dos letras) y con la extensión `.lang`

## - Agradecimientos a
* **[PlatformIO](http://www.platformio.org)**: Ivan Kravets
* **Traducción al Koreano:** @gro
* **Traducción al Chino :** @chkb123456
* **Tranducción al Francés:** @Alnoa
* **Contribuidor de código:** @goolic

## Donar
Apoya el código libre, si te gustó este plugin y quieres aportar con un granito de arena para poder continuar con el desarrollo, hazlo a través de [este link](https://gratipay.com/~gepd/)

Si tienes algun problema o quieres contactarme: <gepd@outlook.com>

## Licencia
Derechos de Autor 2015-2016 GEPD <gepd@outlook.com>

Deviot está licenciado con la licencia permisiva Apache 2.0. Esto significa que tú puedes usarlo personal y comercialmente libre de cargos.

[Leer](https://github.com/gepd/Deviot/blob/master/LICENCE) el archivo de licencia completo.