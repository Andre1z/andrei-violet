<?php
session_start();
require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

// Recuperar las sesiones de chat existentes (tabla: chats)
try {
    $stmt = $db->query("SELECT * FROM chats ORDER BY last_updated DESC");
    $chatSessions = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) {
    $chatSessions = [];
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Chatbot andrei-violet</title>
    <!-- Se carga el CSS externo -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <!-- Sidebar: panel lateral izquierdo -->
    <div id="sidebar">
        <header>
            <!-- Botón para ocultar/mostrar el sidebar -->
            <button id="btn-hide" title="Ocultar panel">&#x2190;</button>
            <!-- Botón para crear un nuevo chat -->
            <button id="btn-new-chat" title="Nuevo chat">&#x2795;</button>
        </header>
        <div id="chat-session-list">
            <?php if (!empty($chatSessions)): ?>
                <?php foreach($chatSessions as $session): ?>
                    <div class="chat-session" data-chat-id="<?php echo $session['id']; ?>">
                        Chat <?php echo $session['id']; ?><br>
                        <?php echo date("d/m/Y H:i", strtotime($session['last_updated'])); ?>
                    </div>
                <?php endforeach; ?>
            <?php else: ?>
                <p>No hay chats iniciados.</p>
            <?php endif; ?>
        </div>
    </div>

    <!-- Área principal del chat -->
    <div id="chat-area">
        <div class="chat-container">
            <header class="chat-header">
                <h1>Chatbot andrei-violet</h1>
            </header>
            <div class="chat-messages" id="chat-messages">
                <!-- Aquí se cargarán los mensajes de la sesión actual -->
            </div>
            <div class="chat-input">
                <form id="chat-form" method="post" action="chat_process.php">
                    <input type="text" name="message" id="message" placeholder="Escribe tu mensaje aquí…" autocomplete="off" required>
                    <button type="submit">Enviar</button>
                </form>
            </div>
        </div>
    </div>

    <!-- Se carga el JavaScript externo -->
    <script src="js/main.js"></script>
</body>
</html>