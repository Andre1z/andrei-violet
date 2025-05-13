<?php
session_start();
header('Content-Type: application/json');

require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

// Se acepta solo el método POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['error' => 'Método no permitido']);
    exit();
}

try {
    // Se inserta una nueva sesión en la tabla 'chats'
    // La sentencia utiliza datetime('now') de SQLite para establecer los valores actuales
    $stmt = $db->prepare("INSERT INTO chats (started_at, last_updated) VALUES (datetime('now'), datetime('now'))");
    $stmt->execute();
    
    // Se obtiene el identificador de la nueva sesión de chat
    $chat_id = $db->lastInsertId();
    
    // Se retorna el chat_id en formato JSON para que el frontend lo use
    echo json_encode(['chat_id' => $chat_id]);
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
exit();