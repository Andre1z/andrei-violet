<?php
session_start();
header('Content-Type: application/json');

require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

// Solo se aceptan peticiones POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['error' => 'Método no permitido']);
    exit();
}

// Se obtiene la información enviada en formato JSON
$data = json_decode(file_get_contents("php://input"), true);
if (!isset($data['chat_id']) || empty($data['chat_id'])) {
    echo json_encode(['error' => 'chat_id no especificado']);
    exit();
}

$chat_id = intval($data['chat_id']);

try {
    // Primero se eliminan los mensajes asociados a la sesión del chat
    $stmt = $db->prepare("DELETE FROM messages WHERE chat_id = :chat_id");
    $stmt->execute([':chat_id' => $chat_id]);

    // Después se elimina la sesión de chat
    $stmt = $db->prepare("DELETE FROM chats WHERE id = :chat_id");
    $stmt->execute([':chat_id' => $chat_id]);

    echo json_encode(['success' => true]);
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
exit();