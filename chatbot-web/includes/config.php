<?php
/**
 * config.php
 *
 * Archivo de configuración global para el proyecto chatbot andrei-violet.
 * Aquí se configuran parámetros como la visualización de errores, zona horaria
 * y la ruta a la base de datos.
 */

// Habilitar la visualización de errores para entornos de desarrollo
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Definir la ruta al archivo SQLite
// Se asume que el archivo database.sqlite se encuentra en chatbot-web/data/
define('DB_PATH', __DIR__ . '/../data/database.sqlite');

// Configurar zona horaria (ajústala según tu ubicación; aquí se usa una zona para España)
date_default_timezone_set('Europe/Madrid');

// Puedes agregar aquí otras configuraciones globales según evolucione el proyecto