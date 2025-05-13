<?php
// create_chats_table.php

require_once 'includes/config.php';
require_once 'includes/db.php';

try {
    // Sentencia SQL para crear la tabla 'chats'
    $sql = "
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ";

    // Ejecuta la sentencia SQL
    $db->exec($sql);
    echo "La tabla 'chats' ha sido creada exitosamente.";
} catch (PDOException $e) {
    echo "Error al crear la tabla 'chats': " . $e->getMessage();
}