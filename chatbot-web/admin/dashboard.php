<?php
session_start();

// Verificar que el usuario esté autenticado como administrador
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    // Si no está autenticado, redirige a la página de login (debes crear login.php)
    header("Location: login.php");
    exit();
}

// Incluir configuraciones y funciones comunes
require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

// Ejemplo: Obtener estadísticas, como el número de usuarios registrados
$totalUsuarios = 0;
try {
    $stmt = $db->query("SELECT COUNT(*) as total FROM users");
    $fila = $stmt->fetch(PDO::FETCH_ASSOC);
    $totalUsuarios = $fila['total'];
} catch (Exception $e) {
    // Registro de errores o notificación (para desarrollo)
    $totalUsuarios = "Error: " . $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Administrador - Chatbot andrei-violet</title>
    <!-- Puedes ajustar o incluir un CSS específico para el panel de administración -->
    <link rel="stylesheet" href="../public/css/style.css">
    <style>
        /* Estilos básicos para el panel de administración */
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        header {
            background: #333;
            color: #fff;
            padding: 15px;
            text-align: center;
        }
        .dashboard {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: #fff;
            border-radius: 5px;
        }
        nav ul {
            list-style: none;
            display: flex;
            padding: 0;
            justify-content: center;
            margin: 0 0 20px 0;
        }
        nav ul li {
            margin: 0 15px;
        }
        nav ul li a {
            text-decoration: none;
            color: #333;
            font-weight: bold;
        }
        .stats {
            margin-bottom: 20px;
            padding: 10px;
            background: #e7e7e7;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <header>
        <h1>Panel de Administración - Chatbot andrei-violet</h1>
    </header>
    <div class="dashboard">
        <nav>
            <ul>
                <li><a href="dashboard.php">Inicio</a></li>
                <li><a href="manage_users.php">Usuarios</a></li>
                <li><a href="manage_content.php">Contenido</a></li>
                <li><a href="logout.php">Cerrar Sesión</a></li>
            </ul>
        </nav>
        <section class="stats">
            <h2>Estadísticas</h2>
            <p>Total de usuarios registrados: <?php echo htmlspecialchars($totalUsuarios); ?></p>
            <!-- Puedes incluir más estadísticas según tu implementación -->
        </section>
        <section>
            <h2>Bienvenido, <?php echo isset($_SESSION['admin_name']) ? htmlspecialchars($_SESSION['admin_name']) : 'Administrador'; ?></h2>
            <p>
                Utiliza el menú de navegación para gestionar usuarios, administrar contenido y revisar
                la actividad general del chatbot.
            </p>
        </section>
    </div>
</body>
</html>