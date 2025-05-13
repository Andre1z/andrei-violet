<?php
session_start();
header('Content-Type: application/json');

// Incluir configuración, conexión y funciones comunes
require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

// Si se recibe un mensaje vía POST
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['message'])) {
    // Se sanitiza la entrada para evitar inyección de código
    $userMessage = sanitizeInput($_POST['message']);
    
    try {
        // Se busca una respuesta que coincida exacta con el disparador ingresado
        $stmt = $db->prepare("SELECT response_text FROM content WHERE trigger_word = :trigger LIMIT 1");
        $stmt->execute([':trigger' => $userMessage]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($result) {
            $reply = $result['response_text'];
        } else {
            // Respuesta por defecto si no se encuentra coincidencia
            $reply = "Lo siento, no tengo una respuesta para esa pregunta.";
        }
    } catch (Exception $e) {
        // En caso de error, se retorna el mensaje del error (útil para depuración)
        $reply = "Error: " . $e->getMessage();
    }
    
    // Se envía la respuesta en formato JSON al frontend
    echo json_encode(['reply' => $reply]);
    exit();
}

// Si no se recibe un mensaje correctamente, se retorna un mensaje genérico
echo json_encode(['reply' => 'No se recibió mensaje.']);
exit();