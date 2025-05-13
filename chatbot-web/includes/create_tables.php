<?php
require_once 'includes/config.php';
require_once 'includes/db.php';

try {
    $sql = "
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ";
    $db->exec($sql);
    echo "La tabla 'users' se ha creado exitosamente.";
} catch (PDOException $e) {
    echo "Error creando la tabla: " . $e->getMessage();
}