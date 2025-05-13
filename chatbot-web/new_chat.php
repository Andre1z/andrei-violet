<?php
// new_chat.php
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

try {
    // Insertamos una nueva sesión de chat en la tabla "chats".
    // Se asume que la tabla "chats" tiene la siguiente estructura:
    // id INTEGER PRIMARY KEY AUTOINCREMENT,
    // started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    // last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    $stmt = $db->prepare("INSERT INTO chats (started_at, last_updated) VALUES (datetime('now'), datetime('now'))");
    $stmt->execute();
    
    // Obtenemos el identificador del chat recién creado
    $chat_id = $db->lastInsertId();
    
    // Retornamos el chat_id en formato JSON
    echo json_encode(['chat_id' => $chat_id]);
} catch (Exception $e) {
    // En caso de error, se retorna un mensaje informando del error
    echo json_encode(['error' => $e->getMessage()]);
}

exit();