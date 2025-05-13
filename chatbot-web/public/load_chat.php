<?php
session_start();
header('Content-Type: application/json');

require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

// Se requiere que se proporcione el parámetro GET "chat_id"
if (!isset($_GET['chat_id']) || empty($_GET['chat_id'])) {
    echo json_encode(['error' => 'chat_id no proporcionado']);
    exit();
}

$chat_id = intval($_GET['chat_id']);

try {
    // Se consulta la tabla messages para obtener los mensajes de la sesión dada
    // Se ordena de forma ascendente según la fecha de envío para conservar el orden
    $stmt = $db->prepare("SELECT sender, message, sent_at FROM messages WHERE chat_id = :chat_id ORDER BY sent_at ASC");
    $stmt->execute([':chat_id' => $chat_id]);
    
    $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode(['messages' => $messages]);
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
exit();