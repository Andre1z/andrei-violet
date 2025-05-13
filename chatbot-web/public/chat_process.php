<?php
session_start();
header('Content-Type: application/json');

require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_POST['message'])) {
    echo json_encode(['reply' => 'No se recibió mensaje.']);
    exit();
}

$chat_id = isset($_POST['chat_id']) ? intval($_POST['chat_id']) : null;
$message = sanitizeInput($_POST['message']);

// Inserta el mensaje del usuario en la tabla messages
try {
    $stmt = $db->prepare("INSERT INTO messages (chat_id, sender, message, sent_at) VALUES (:chat_id, 'user', :message, datetime('now'))");
    $stmt->execute([':chat_id' => $chat_id, ':message' => $message]);
    
    // Actualiza la última actualización del chat
    $stmt = $db->prepare("UPDATE chats SET last_updated = datetime('now') WHERE id = :chat_id");
    $stmt->execute([':chat_id' => $chat_id]);
} catch (Exception $e) {
    echo json_encode(['reply' => 'Error almacenando el mensaje del usuario: ' . $e->getMessage()]);
    exit();
}

// Busca una respuesta predefinida (por ejemplo, búsqueda exacta)
try {
    $stmt = $db->prepare("SELECT response_text FROM content WHERE trigger_word = :trigger LIMIT 1");
    $stmt->execute([':trigger' => $message]);
    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($result) {
        $reply = $result['response_text'];
    } else {
        $reply = "Lo siento, no tengo una respuesta para esa pregunta.";
    }
} catch (Exception $e) {
    echo json_encode(['reply' => 'Error consultando la respuesta: ' . $e->getMessage()]);
    exit();
}

// Inserta la respuesta del bot
try {
    $stmt = $db->prepare("INSERT INTO messages (chat_id, sender, message, sent_at) VALUES (:chat_id, 'bot', :reply, datetime('now'))");
    $stmt->execute([':chat_id' => $chat_id, ':reply' => $reply]);
    
    // Actualiza last_updated nuevamente
    $stmt = $db->prepare("UPDATE chats SET last_updated = datetime('now') WHERE id = :chat_id");
    $stmt->execute([':chat_id' => $chat_id]);
} catch (Exception $e) {
    echo json_encode(['reply' => 'Error almacenando el mensaje del bot: ' . $e->getMessage()]);
    exit();
}

echo json_encode(['reply' => $reply]);
exit();