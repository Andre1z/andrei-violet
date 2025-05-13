<?php
// create_admin.php
require_once 'includes/config.php';
require_once 'includes/db.php';

// Datos del usuario admin.
$username = 'admin';
$email    = 'admin@admin.com';
$password = 'admin'; // Contraseña en texto plano

// Encriptar la contraseña.
$hashedPassword = password_hash($password, PASSWORD_DEFAULT);

try {
    // Insertar el usuario admin en la tabla users.
    $stmt = $db->prepare("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)");
    $stmt->execute([
        ':username' => $username,
        ':email'    => $email,
        ':password' => $hashedPassword,
    ]);
    echo "El usuario admin ha sido creado correctamente.";
} catch (PDOException $e) {
    // Si el usuario ya existe o ocurre otro error, se muestra el mensaje.
    echo "Error al crear el usuario admin: " . $e->getMessage();
}