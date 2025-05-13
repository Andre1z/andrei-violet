<?php
// Inicia la sesión (útil para conservar estados del usuario)
session_start();
// Si fuera necesario, se puede incluir una configuración general, por ejemplo:
// require_once '../includes/config.php';
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot andrei-violet</title>
    <!-- Incluye la hoja de estilos -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="chat-container">
        <!-- Encabezado del Chat -->
        <header class="chat-header">
            <h1>Chatbot andrei-violet</h1>
        </header>
        
        <!-- Área donde se mostrarán los mensajes -->
        <div class="chat-messages" id="chat-messages">
            <!-- Los mensajes se cargarán dinámicamente aquí -->
        </div>
        
        <!-- Formulario para enviar mensajes -->
        <div class="chat-input">
            <form id="chat-form" method="post" action="chat_process.php">
                <input 
                    type="text" 
                    name="message" 
                    id="message" 
                    placeholder="Escribe tu mensaje aquí…" 
                    autocomplete="off"
                    required>
                <button type="submit">Enviar</button>
            </form>
        </div>
    </div>
    
    <!-- Incluye el archivo JavaScript que manejará los eventos del chat -->
    <script src="js/main.js"></script>
</body>
</html>