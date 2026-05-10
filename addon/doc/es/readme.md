# Link Library #

Autor: Ibrahim Hamadeh  
Descargar [Versión 2.2.6][1]  
Compatibilidad con NVDA: 2021.1 en adelante  

Este complemento ayuda al usuario a organizar sus enlaces o marcadores al estilo de una biblioteca.  
Desde el diálogo principal de bibliotecas, puedes añadir, renombrar o eliminar cualquiera de ellas.  
Si ya tienes bibliotecas, elige la biblioteca o categoría que te guste y pulsa Intro sobre ella.  
En el diálogo abierto, tendrás todos los enlaces de esa categoría en una lista y acceso a la URL de origen y a la información "acerca de" de cada enlace, si está presente.  
Este complemento no viene con un gesto o atajo asignado por defecto.  
Como siempre, puedes añadir un gesto o cambiar el existente yendo a:  
Menú NVDA > Preferencias > Gestos de entrada > Link Library.  

## Uso ##

*	Tras asignar un gesto al complemento, usando ese gesto o atajo puedes abrir el diálogo principal del complemento.  
*	Se abrirá un diálogo listando todas las bibliotecas o categorías de enlaces encontradas.  
*	Al principio no se encuentran bibliotecas; está vacío, listo para alojar las bibliotecas que desees establecer.  
*	Tabulando en ese diálogo, puedes renombrar, eliminar o añadir cualquier biblioteca o categoría de enlaces en cualquier momento.  
*	Teniendo algunas bibliotecas, sitúate en la lista sobre la que elijas y pulsa Intro.   
*	Se abrirá un diálogo para esa biblioteca, mostrando todos los enlaces (nombre o etiqueta de los enlaces) en una lista.  
*	Al principio la biblioteca está vacía y no hay enlaces en ella.  
*	Pulsamos el menú contextual (Shift + F10), o el menú emergente, o la tecla de aplicaciones, para añadir un enlace introduciendo la URL, etiqueta y opcionalmente el "acerca de" del enlace.  
*	Situado sobre cualquier enlace de esta lista, pulsar Intro lo abrirá con el navegador predeterminado.  
*	Tabulando en ese diálogo puedes acceder al "acerca de" del enlace (información sobre el mismo) si está presente, un botón para mostrar la URL de origen, y otro botón que te da la opción de abrir el enlace con varios navegadores si se encuentran en tu ordenador.  
*	Y usando el control de filtro allí mismo, puedes filtrar los enlaces que contengan palabras o frases específicas en la biblioteca.
*	Sitúate sobre el enlace que quieras en esta lista y pulsa el menú contextual.  
*	Desde allí puedes añadir, editar, mover el enlace a otra biblioteca, eliminar ese enlace o todos.  
*	Ahora, ¿quieres importar una biblioteca JSON, o exportar cualquier biblioteca como archivo JSON o HTML? Sí, puedes hacerlo, e incluso si quieres importar todos los marcadores de Firefox como JSON, también puedes hacerlo.
*	Por ejemplo, para exportar una biblioteca, sitúate sobre la que quieras exportar y pulsa el menú contextual, baja una vez con la flecha hasta "Exportar biblioteca como", elige el tipo de archivo que quieres exportar (JSON o HTML) y pulsa Intro.  
*	Se abrirá un diálogo para elegir la carpeta a la que quieres exportar; elige la carpeta y pulsa Intro o navega hasta el botón "Seleccionar carpeta" y púlsalo.  
*	Eso es todo, se mostrará un mensaje de información indicándote que la biblioteca ha sido exportada, ¡felicidades!  
*	Otra cosa fantástica: si exportas una biblioteca como HTML, puedes incluir los enlaces de ese archivo en los marcadores de Firefox si quieres.  
*	Solo abre Firefox, desde el menú de marcadores elige "Mostrar todos los marcadores" (Control+Shift+B).  
*	En el menú de la nueva ventana, ve al submenú "Importar y respaldar", luego a "Importar marcadores desde HTML…" y pulsa Intro.  
*	Navega por el diálogo abierto hasta el archivo HTML y selecciónalo. Después de eso, se encontrará una entrada o carpeta con el mismo nombre de la biblioteca importada en el menú de marcadores de Firefox, incluyendo todos los enlaces de la biblioteca importada.  
*	Mencionado al final, pero quizás lo más importante, es que tienes la capacidad de elegir el lugar de los archivos de datos de tu complemento.  
*	Primero, al instalar el complemento, aparecerá un cuadro de mensaje preguntándote si aceptas crear la carpeta que aloja los datos del complemento en tu directorio de usuario.  
*	Puedes, si lo deseas, pulsar "Cancelar" y elegir el directorio requerido para alojar los archivos de datos más tarde desde el diálogo de configuración del complemento en el menú de preferencias.  
*	Ve al menú NVDA > Preferencias > Link Library > Link Library Setting..., y abre el diálogo de ajustes.  
*	Puedes, mediante el botón "Añadir nueva ruta", añadir una o más rutas, o eliminar cualquier ruta añadida mediante el botón "Eliminar".
*	Tras elegir la nueva ruta predeterminada para los archivos de datos o bibliotecas en ese diálogo.  
*	Si quieres que sea permanente, tienes que guardar la configuración pulsando Control+NVDA+C, especialmente si tu configuración no está establecida para guardarse al salir en el diálogo de opciones generales.  
*	Cabe notar que crear la carpeta para alojar los datos en el directorio de usuario ayuda a que todas las instancias del complemento en el ordenador puedan compartir los mismos archivos o base de datos.  
*	Y elegir otra ruta como Dropbox, por ejemplo, dará al usuario la capacidad de compartir la misma carpeta o base de datos con instancias del complemento en otro ordenador que use la misma cuenta de Dropbox.  

## Función de sub-bibliotecas ##

Puedes añadir sub-bibliotecas a cualquier biblioteca si lo deseas.

*	Abre la biblioteca que quieras.
*	Pulsa el menú contextual, emergente o de aplicaciones.
*	Genial, ahora tienes desde allí la opción de añadir, renombrar o eliminar cualquier sub-biblioteca si están presentes.
¡Fácil, ¿verdad? ¡Disfruta!

## Añadir un enlace al vuelo ##

Característica maravillosa: Añadir enlace de página web al vuelo.

Para usar esta función, primero tienes que asignarle un gesto o atajo yendo a: Menú NVDA (NVDA+N) / Preferencias / Gestos de entrada / Link Library / Añadir el enlace y título de la página web al vuelo a la biblioteca que elijas.

Ahora, mientras navegas por la red, si quieres añadir una página a cualquier biblioteca en el complemento Link Library puedes hacerlo. Desde cualquier lugar de la página que te guste, pulsa el gesto o atajo para esta función; se abrirá una ventana que dice "Añadir enlace y título de página web a la biblioteca". En ella hay un botón que dice "Elegir biblioteca:", pulsa el botón y, desde el menú emergente que aparece, elige la biblioteca que quieras y pulsa Intro.

Eso es todo, el enlace o URL de la página web se añade a la biblioteca con su título como etiqueta, y oirás un mensaje de confirmación indicándolo. Realmente algo hermoso.

### Cambios para 2.2.6 ###

*	Actualizada la última versión probada para cumplir con el reciente lanzamiento de NVDA 2026.1.
*	En el diálogo de configuración del complemento, en el cuadro combinado que contiene varias rutas para almacenar datos, ahora se muestra la ruta completa del directorio y no solo la etiqueta de la ruta.

### Cambios para 2.2.5 ###

*	Actualizada la traducción al ucraniano, contribuida por [@George-br](https://github.com/George-br).

### Cambios para 2.2.4 ###

*	Corregido un error en la función "Añadir un enlace al vuelo", por lo que ahora puedes añadir un enlace a una biblioteca o sub-biblioteca abierta, lo cual no era posible antes.

### Cambios para 2.2.3 ###

*	Añadida una nueva característica para importar todos los marcadores de Firefox (como archivo JSON), para ser incluidos en el complemento; puedes acceder a ello a través de una opción en el menú contextual mientras estás en la lista de bibliotecas.

### Cambios para 2.2.2 ###

*	Ahora es posible exportar una biblioteca con sus sub-bibliotecas como archivo HTML y luego, si lo deseas, integrarla en los marcadores de Firefox.

### Cambios para 2.2.1 ###

*	Actualizados los archivos de plantilla del complemento y uso de GitHub Actions para construir el complemento en lugar de AppVeyor.

### Cambios para 2.2 ###

*	Corregido un ligero error al extraer el título de la página web en la función de añadir al vuelo.

### Cambios para 2.1.9 ###

*	Se hace posible añadir un enlace de página web al vuelo; asigna un gesto a esta función y púlsalo en cualquier página. En el menú emergente elige la biblioteca y el enlace será añadido con el título de la página como etiqueta.

### Cambios para 2.1.8 ###

*	Añadida la opción de abrir el enlace en modo privado para Firefox, Chrome y Edge; puedes acceder a ello tras pulsar el botón "Abrir enlace con" en el diálogo del enlace.

### Cambios para 2.1.6 ###

*	Actualizada la traducción al turco por Umut KORKMAZ.

### Cambios para 2.1.5 ###

*	Las cadenas "Tiene sub-biblioteca" y "Sub-biblioteca" ahora son traducibles.
*	Ahora es posible eliminar una biblioteca con sub-bibliotecas; era un error corregido, reportado por Umut KORKMAZ.
*	Al intentar eliminar una biblioteca que tiene sub-bibliotecas, ahora el mensaje advertirá que vas a eliminar una biblioteca junto con sus sub-bibliotecas para ser claro al respecto.

### Cambios para 2.1.4 ###

*	Añadida la función de sub-biblioteca; el usuario ahora puede añadir a una biblioteca una sub-biblioteca, renombrarla o eliminarla.

### Cambios para 2.1.3 ###

*	Añadido el navegador Yandex a la lista de navegadores con los que puedes abrir el enlace. Gracias al usuario que lo solicitó.

### Cambios para 2.1.2 ###

*	Añadida localización al ruso por Kostenkov-2021.
*	Actualizada la traducción al ucraniano por VovaMobile.

### Cambios para 2.1.1 ###

*	Actualizada la última versión probada, por lo que ahora el complemento es compatible con NVDA 2024.1.

### Cambios para 2.1 ###

*	Se crea un cuadro combinado en el diálogo de configuración del complemento para elegir una acción tras activar un enlace, en lugar de una casilla de verificación.  
Ahora puedes elegir entre: No hacer nada, Cerrar solo la ventana de la biblioteca, o Cerrar la ventana principal del complemento tras activar un enlace.
*	Ahora el título de la ventana principal del complemento no incluye la ruta completa de los archivos de datos, sino solo el directorio padre.  
Si tu carpeta de datos está por ejemplo en la carpeta Documentos, el título ya no será:  
"Link Library - C:\users\...\Documents", sino que en su lugar será: "Link Library - Documents".

### Cambios para 2.0 ###

*	Añadido idioma Chino Simplificado.

### Cambios para 1.9 ###

*	Actualizada la última versión probada, haciendo el complemento compatible con NVDA 2023.1.

### Cambios para 1.8 ###

*	Añadido un control de filtro en el diálogo de cada biblioteca; usándolo, el usuario ahora puede filtrar enlaces en la biblioteca que solo contengan palabras o frases específicas, ya sea en la URL o en la etiqueta del enlace.
*	En el diálogo principal de bibliotecas, tras añadir o renombrar una biblioteca, la lista de bibliotecas se ordena ahora alfabéticamente, algo que faltaba anteriormente.

### Cambios para 1.7 ###

*	Añadida traducción al portugués para el complemento.

### Cambios para 1.6 ###

*	Añadida traducción al ucraniano.

### Cambios para 1.5 ###

*	Ahora puedes mover un enlace de una biblioteca a otra; esto se puede lograr a través del menú emergente, luego el ítem "Mover enlace a", y desde el submenú allí puedes elegir la biblioteca y pulsar Intro.

### Cambios para 1.4 ###

*	Ahora, al cerrar una biblioteca abierta mediante la tecla Escape o el botón Cancelar, el foco volverá a la ventana principal de bibliotecas.

### Cambios para 1.3 ###

*	Botón cerrar reemplazado por Aceptar y Cancelar en el diálogo de enlaces, y se hace posible eliminar la biblioteca general en el diálogo de biblioteca.  
*	Cambiada la versión mínima probada del complemento a 2019.3.  
*	Añadida traducción al turco para el complemento.  

### Cambios para 1.2 ###

*	Corrección de un error al activar el menú contextual en la API de NVDA 2021.1.  
*	Eliminado Edge Legacy de "Abrir enlace con" en el diálogo de enlace.  

### Cambios para 1.1 ###

*	Ahora los enlaces en las bibliotecas (es decir, sus etiquetas) se ordenan ignorando mayúsculas y minúsculas.  
*	Durante la importación de una biblioteca JSON, si existe un nombre similar, se preguntará al usuario si desea fusionar las dos bibliotecas o no; si dice No, la biblioteca se importará teniendo un número entre paréntesis como sufijo indicando el número de bibliotecas similares, y si quiere fusionarlas, el archivo importado o existente tendrá los dos diccionarios fusionados en su interior.  

### Cambios para 1.0 ###

*	Cambio de archivos de datos o bibliotecas de .pickle a archivos .json.
*	En el título del diálogo de Link Library, ahora se añade la etiqueta de la ruta elegida por el usuario para almacenar los archivos de datos.  

### Cambios para 0.5 ###

*	Añadido un diálogo en los ajustes del complemento para permitir al usuario añadir o elegir el directorio en el que desea alojar el archivo de datos del complemento.  
*	Así que ahora puede mantener la ruta por defecto, que es el directorio de usuario, o elegir desde el diálogo de ajustes la ruta que desee.  

### Cambios para 0.4 ###

*	Hecho el complemento compatible con Python 3.  

### Cambios para 0.2 ###

*	Se establece como único lugar para guardar y recuperar datos una carpeta llamada "linkLibrary-addonFiles" en el directorio del usuario. De modo que será utilizada por todas las instancias del complemento en versiones instaladas o portátiles de NVDA.

### Cambios para 0.1 ###

*	Versión inicial.

### Contribuciones ###

Muy agradecido a:
*	Umut KORKMAZ, por el apoyo en la traducción al turco.
*	VovaMobile, por el apoyo en la traducción al ucraniano.

### Contacto ###

 en caso de cualquier error o sugerencia puedes [enviarme un correo electrónico.](mailto:ibra.hamadeh@hotmail.com)

[1]: https://github.com/ibrahim-s/linkLibrary/releases/download/2.2.6/linkLibrary-2.2.6.nvda-addon
