# Chatbot andrei-violet

## Descripción:
-------------
Chatbot andrei-violet es una aplicación web de mensajería y chat interactiva desarrollada en PHP y SQLite, con un diseño moderno y minimalista. La aplicación permite crear y gestionar múltiples sesiones de chat, almacenar la conversación en la base de datos y ofrece funcionalidades adicionales como eliminar o compartir un chat a través de opciones accesibles en un modal.

## Características:
-----------------
• Interfaz de chat interactiva con respuestas predefinidas.
• Sidebar que muestra las sesiones de chat creadas.
• Funcionalidad para iniciar un nuevo chat, visualizar las conversaciones previas y gestionarlas.
• Opción de eliminar o compartir un chat mediante un pop-up de opciones.
• Panel de administración (con posibilidad de ampliarlo) para gestionar usuarios y contenido.
• Diseño moderno y minimalista con colores vibrantes y transiciones sutiles.

## Requisitos:
-----------
• PHP 7.x o superior.
• SQLite instalado (la base de datos se maneja usando SQLite).
• Servidor web (Apache, Nginx, u otro compatible con PHP).
• Acceso a la terminal o a un navegador web para ejecutar scripts de creación de tablas.

## Estructura del Proyecto:
-------------------------
```
chatbot-web/
├── includes/
│    ├── config.php           - Configuración general y variables (ej. DB_PATH).
│    ├── db.php               - Conexión PDO a la base de datos.
│    └── functions.php        - Funciones auxiliares (ej. sanitizeInput).
├── public/
│    ├── css/
│    │     └── style.css       - Hojas de estilo con el diseño moderno.
│    ├── js/
│    │     └── main.js         - Lógica de interacción y llamadas AJAX.
│    ├── index.php            - Interfaz principal del chat.
│    ├── chat_process.php     - Procesa los mensajes enviados y gestiona respuestas.
│    ├── new_chat.php         - Crea una nueva sesión de chat.
│    ├── load_chat.php        - Carga la conversación de un chat existente.
│    └── delete_chat.php      - Elimina una sesión de chat y sus mensajes.
└── create_tables/           - (Opcional) Scripts para crear las tablas:
         ├── create_chats_table.php
         ├── create_messages_table.php
         └── create_users_table.php   (si se requiere para el panel de administración)
```

## Instalación y Configuración:
----------------------------
1. Clona o descarga el proyecto en tu servidor web.
2. Configura el archivo **includes/config.php** para definir la ruta a tu base de datos (por ejemplo, una constante DB_PATH).
3. Ejecuta los scripts de creación de tablas:
   - Abre tu navegador y accede a: 
         http://localhost/andrei-violet/create_chats_table.php
         http://localhost/andrei-violet/create_messages_table.php
         (y create_users_table.php si corresponde)
   Esto creará las tablas "chats", "messages" (y "users", si aplica) en tu base de datos.
4. Accede al proyecto mediante la URL:
         http://localhost/andrei-violet/public/index.php
5. Utiliza la interfaz para crear, gestionar y conversar a través del chatbot.

## Uso:
-----
• Al ingresar a la interfaz, el sidebar muestra las sesiones de chat existentes.
• Usa el botón de "Nuevo chat" (botón con el signo "+") para iniciar una sesión nueva.
• Selecciona un chat del sidebar para visualizar su historial.
• Escribe un mensaje en el área principal; el sistema lo procesará y el chatbot responderá basado en disparadores.
• Cada sesión muestra un botón de opciones (representado por “···”) junto a la fecha, que te permitirá abrir un pop-up con las opciones de eliminar o compartir el chat.
• La funcionalidad de "Eliminar chat" se ocupa de borrar la sesión y todos sus mensajes de la base de datos.
• La opción "Compartir chat" permite copiar información de la sesión al portapapeles para facilitar su difusión.

## Tecnologías Utilizadas:
-------------------------
• Lenguajes: PHP, HTML, CSS, JavaScript.
• Base de Datos: SQLite.
• Diseño Responsive y moderno, con gradientes y transiciones.

## Licencia:
----------
Este proyecto se distribuye bajo la Licencia MIT.

## Autor:
-------
Creado por Andrei Buga – Chatbot andrei-violet

## Notas Adicionales:
-------------------
• Asegúrate de que el servidor web tenga permisos adecuados para crear y modificar la base de datos.
• Puedes ampliar la funcionalidad del chatbot agregando nuevos disparadores y respuestas en la tabla "content" o integrando lógica adicional en el backend.
• Si deseas implementar nuevas características (p.ej., autenticación de usuarios, panel de administración ampliado, etc.), puedes extender los archivos existentes y complementar la documentación.