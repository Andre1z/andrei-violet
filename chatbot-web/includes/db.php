<?php
/**
 * db.php
 *
 * Archivo de conexión a la base de datos SQLite para el proyecto chatbot andrei-violet.
 * Se utiliza PDO para conectarse a la base de datos definida en DB_PATH (configurado en config.php).
 */

require_once 'config.php';

try {
    // Establece la conexión a la base de datos SQLite
    $db = new PDO("sqlite:" . DB_PATH);
    
    // Configurar errores para que sean manejados como excepciones
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Configurar el mode de recuperación de datos en forma de array asociativo
    $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    // En un entorno de producción puedes registrar el error y mostrar un mensaje genérico
    die("Error en la conexión a la base de datos: " . $e->getMessage());
}