<?php
// create_content_table.php
require_once 'includes/config.php';
require_once 'includes/db.php';

try {
    $sql = "
    CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger_word TEXT NOT NULL,
        response_text TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ";
    $db->exec($sql);
    echo "La tabla 'content' se ha creado exitosamente.";
} catch (PDOException $e) {
    echo "Error al crear la tabla 'content': " . $e->getMessage();
}