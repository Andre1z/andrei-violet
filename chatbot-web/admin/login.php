<?php
session_start();

// Si ya está autenticado, redirige directamente al dashboard
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    header("Location: dashboard.php");
    exit();
}

require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

$feedback = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Se sanitizan y recogen las credenciales del formulario
    $username = sanitizeInput($_POST['username']);
    $password = $_POST['password']; // Se procesa sin sanitizar, para verificar con la clave hasheada

    if (!empty($username) && !empty($password)) {
        try {
            // Se consulta la base de datos para buscar al usuario
            $stmt = $db->prepare("SELECT * FROM users WHERE username = :username LIMIT 1");
            $stmt->execute([':username' => $username]);
            $user = $stmt->fetch();
            if ($user) {
                // Se verifica la contraseña utilizando password_verify()
                if (password_verify($password, $user['password'])) {
                    // En este ejemplo se asume que el usuario "admin" es el único con permisos administrativos.
                    if ($username === "admin") {
                        $_SESSION['admin_logged_in'] = true;
                        $_SESSION['admin_name'] = $user['username'];
                        header("Location: dashboard.php");
                        exit();
                    } else {
                        $feedback = "No tiene permisos de administrador.";
                    }
                } else {
                    $feedback = "Credenciales incorrectas.";
                }
            } else {
                $feedback = "El usuario no existe.";
            }
        } catch (Exception $e) {
            $feedback = "Error al verificar credenciales: " . $e->getMessage();
        }
    } else {
        $feedback = "Por favor, rellene todos los campos.";
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login - Panel de Administración</title>
    <link rel="stylesheet" href="../public/css/style.css">
    <style>
        /* Estilos específicos para la página de login */
        .login-container {
            max-width: 400px;
            margin: 80px auto;
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .login-container h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        .login-container form input[type="text"],
        .login-container form input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        .login-container form button {
            width: 100%;
            padding: 10px;
            background: #333;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .login-container form button:hover {
            opacity: 0.9;
        }
        .feedback {
            text-align: center;
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Iniciar Sesión</h2>
        <?php if (!empty($feedback)) : ?>
            <div class="feedback alert error"><?php echo htmlspecialchars($feedback); ?></div>
        <?php endif; ?>
        <form method="post" action="login.php">
            <label for="username">Nombre de Usuario:</label>
            <input type="text" name="username" id="username" required placeholder="Ingrese su usuario">

            <label for="password">Contraseña:</label>
            <input type="password" name="password" id="password" required placeholder="Ingrese su contraseña">

            <button type="submit">Ingresar</button>
        </form>
    </div>
</body>
</html>