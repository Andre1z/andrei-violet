<?php
// create_messages_table.php

require_once 'includes/config.php';
require_once 'includes/db.php';

try {
    // Sentencia SQL para crear la tabla 'messages'
    $sql = "
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chats(id)
    );
    ";

    // Ejecuta la sentencia SQL mediante PDO
    $db->exec($sql);
    echo "La tabla 'messages' ha sido creada exitosamente.";
} catch (PDOException $e) {
    echo "Error al crear la tabla 'messages': " . $e->getMessage();
}