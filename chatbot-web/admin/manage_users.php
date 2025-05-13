<?php
session_start();

// Verificar que el usuario esté autenticado como administrador
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php");
    exit();
}

// Incluir configuraciones y funciones comunes
require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

$feedback = "";

// Procesamiento para eliminar un usuario, si se obtiene el parámetro "delete"
if (isset($_GET['delete'])) {
    $deleteId = intval($_GET['delete']);
    try {
        $stmt = $db->prepare("DELETE FROM users WHERE id = :id");
        $stmt->execute([':id' => $deleteId]);
        $feedback = "Usuario eliminado con éxito.";
    } catch (Exception $e) {
        $feedback = "Error al eliminar usuario: " . $e->getMessage();
    }
}

// Procesamiento para agregar un nuevo usuario
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action']) && $_POST['action'] === 'add') {
        $username = isset($_POST['username']) ? trim($_POST['username']) : "";
        $email    = isset($_POST['email']) ? trim($_POST['email']) : "";
        $password = isset($_POST['password']) ? trim($_POST['password']) : "";

        if (!empty($username) && !empty($email) && !empty($password)) {
            // Es recomendable almacenar la contraseña encriptada
            $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
            try {
                $stmt = $db->prepare("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)");
                $stmt->execute([
                    ':username' => $username,
                    ':email'    => $email,
                    ':password' => $hashedPassword
                ]);
                $feedback = "Usuario agregado con éxito.";
            } catch (Exception $e) {
                $feedback = "Error al agregar usuario: " . $e->getMessage();
            }
        } else {
            $feedback = "Por favor, rellene todos los campos.";
        }
    }
}

// Consulta: obtener la lista de usuarios
try {
    $stmt = $db->query("SELECT * FROM users ORDER BY id DESC");
    $userList = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) {
    $userList = [];
    $feedback = "Error al obtener usuarios: " . $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gestionar Usuarios - Chatbot andrei-violet</title>
    <link rel="stylesheet" href="../public/css/style.css">
    <style>
        /* Estilos básicos para el panel de gestión de usuarios */
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
        .admin-container {
            max-width: 900px;
            margin: 20px auto;
            padding: 20px;
            background: #fff;
            border-radius: 5px;
        }
        nav ul {
            list-style: none;
            display: flex;
            justify-content: center;
            padding: 0;
            margin-bottom: 20px;
        }
        nav ul li {
            margin: 0 15px;
        }
        nav ul li a {
            text-decoration: none;
            color: #333;
            font-weight: bold;
        }
        .feedback {
            padding: 10px;
            margin-bottom: 15px;
            background: #e7e7e7;
            border-radius: 5px;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ccc;
            text-align: left;
        }
        form.add-user input[type="text"],
        form.add-user input[type="email"],
        form.add-user input[type="password"] {
            width: 100%;
            padding: 8px;
            margin: 5px 0 15px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        form.add-user button {
            padding: 10px 20px;
            background: #333;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        form.add-user button:hover {
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <header>
        <h1>Panel de Administración - Chatbot andrei-violet</h1>
    </header>
    <div class="admin-container">
        <nav>
            <ul>
                <li><a href="dashboard.php">Inicio</a></li>
                <li><a href="manage_users.php">Usuarios</a></li>
                <li><a href="manage_content.php">Contenido</a></li>
                <li><a href="logout.php">Cerrar Sesión</a></li>
            </ul>
        </nav>

        <?php if (!empty($feedback)) : ?>
            <div class="feedback"><?php echo htmlspecialchars($feedback); ?></div>
        <?php endif; ?>

        <section>
            <h2>Agregar Nuevo Usuario</h2>
            <form class="add-user" method="post" action="manage_users.php">
                <input type="hidden" name="action" value="add">
                <label for="username">Nombre de Usuario:</label>
                <input type="text" name="username" id="username" placeholder="Introduce el nombre de usuario" required>

                <label for="email">Email:</label>
                <input type="email" name="email" id="email" placeholder="Introduce el email" required>

                <label for="password">Contraseña:</label>
                <input type="password" name="password" id="password" placeholder="Introduce la contraseña" required>

                <button type="submit">Agregar Usuario</button>
            </form>
        </section>

        <section>
            <h2>Lista de Usuarios</h2>
            <?php if (!empty($userList)) : ?>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre de Usuario</th>
                            <th>Email</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($userList as $row) : ?>
                            <tr>
                                <td><?php echo htmlspecialchars($row['id']); ?></td>
                                <td><?php echo htmlspecialchars($row['username']); ?></td>
                                <td><?php echo htmlspecialchars($row['email']); ?></td>
                                <td>
                                    <a href="manage_users.php?delete=<?php echo htmlspecialchars($row['id']); ?>" onclick="return confirm('¿Estás seguro de eliminar este usuario?');">Eliminar</a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else : ?>
                <p>No se encontraron usuarios.</p>
            <?php endif; ?>
        </section>
    </div>
</body>
</html>