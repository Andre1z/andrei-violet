<?php
/**
 * functions.php
 *
 * Archivo de funciones auxiliares para el proyecto chatbot andrei-violet.
 * Aquí se incluyen utilidades comunes para la sanitización de entradas, redirección,
 * validación de datos y generación de mensajes formateados.
 */

/**
 * Sanitiza una cadena de texto eliminando etiquetas HTML y espacios en blanco,
 * convirtiendo caracteres especiales a entidades HTML.
 *
 * @param string $input La cadena a sanitizar.
 * @return string La cadena sanitizada.
 */
function sanitizeInput($input) {
    return htmlspecialchars(strip_tags(trim($input)), ENT_QUOTES, 'UTF-8');
}

/**
 * Redirecciona a una URL especificada y termina la ejecución del script.
 *
 * @param string $url La URL a la que redirigir.
 */
function redirect($url) {
    header('Location: ' . $url);
    exit();
}

/**
 * Valida un correo electrónico utilizando el filtro FILTER_VALIDATE_EMAIL.
 *
 * @param string $email El correo electrónico a validar.
 * @return bool Devuelve true si el correo es válido, false en caso contrario.
 */
function isValidEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

/**
 * Muestra un mensaje en formato HTML con una clase CSS correspondiente al tipo de mensaje.
 *
 * @param string $message El mensaje a mostrar.
 * @param string $type El tipo de mensaje ('success', 'error', 'info'), por defecto 'info'.
 */
function displayMessage($message, $type = 'info') {
    echo "<div class='alert {$type}'>" . sanitizeInput($message) . "</div>";
}

/**
 * Comprueba si la solicitud HTTP actual es de tipo POST.
 *
 * @return bool True si la solicitud es POST, false de lo contrario.
 */
function isPostRequest() {
    return $_SERVER['REQUEST_METHOD'] === 'POST';
}