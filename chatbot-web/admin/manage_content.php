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

// Procesamiento de formularios: Agregar nuevo contenido
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action']) && $_POST['action'] === 'add') {
        $trigger  = isset($_POST['trigger']) ? trim($_POST['trigger']) : "";
        $response = isset($_POST['response']) ? trim($_POST['response']) : "";
  
        if (!empty($trigger) && !empty($response)) {
            try {
                $stmt = $db->prepare("INSERT INTO content (trigger_word, response_text) VALUES (:trigger, :response)");
                $stmt->execute([
                    ':trigger'  => $trigger,
                    ':response' => $response
                ]);
                $feedback = "Contenido agregado con éxito.";
            } catch (Exception $e) {
                $feedback = "Error al agregar contenido: " . $e->getMessage();
            }
        } else {
            $feedback = "Por favor, rellena todos los campos.";
        }
    }
}

// Procesamiento de eliminación: ?delete=ID
if (isset($_GET['delete'])) {
    $deleteId = intval($_GET['delete']);
    try {
        $stmt = $db->prepare("DELETE FROM content WHERE id = :id");
        $stmt->execute([':id' => $deleteId]);
        $feedback = "Contenido eliminado con éxito.";
    } catch (Exception $e) {
        $feedback = "Error al eliminar el contenido: " . $e->getMessage();
    }
}

// Consulta de todo el contenido existente
try {
    $stmt = $db->query("SELECT * FROM content ORDER BY id DESC");
    $contentList = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (Exception $e) {
    $contentList = [];
    $feedback = "Error al obtener el contenido: " . $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Administrar Contenido - Chatbot andrei-violet</title>
    <link rel="stylesheet" href="../public/css/style.css">
    <style>
        /* Estilos básicos para el panel de administración de contenido */
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
        form.add-content {
            margin-bottom: 30px;
        }
        form.add-content input[type="text"],
        form.add-content textarea {
            width: 100%;
            padding: 8px;
            margin: 5px 0 15px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        form.add-content button {
            padding: 10px 20px;
            background: #333;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        form.add-content button:hover {
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
            <h2>Agregar Nuevo Contenido</h2>
            <form class="add-content" method="post" action="manage_content.php">
                <input type="hidden" name="action" value="add">
                <label for="trigger">Disparador:</label>
                <input type="text" name="trigger" id="trigger" placeholder="Ej. hola, saludos" required>

                <label for="response">Respuesta Predefinida:</label>
                <textarea name="response" id="response" rows="3" placeholder="Ej. ¡Hola! ¿En qué puedo ayudarte?" required></textarea>

                <button type="submit">Agregar Contenido</button>
            </form>
        </section>

        <section>
            <h2>Contenido Existente</h2>
            <?php if (!empty($contentList)) : ?>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Disparador</th>
                            <th>Respuesta</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($contentList as $row) : ?>
                            <tr>
                                <td><?php echo htmlspecialchars($row['id']); ?></td>
                                <td><?php echo htmlspecialchars($row['trigger_word']); ?></td>
                                <td><?php echo htmlspecialchars($row['response_text']); ?></td>
                                <td>
                                    <!-- Podrías agregar un enlace para editar en el futuro -->
                                    <a href="manage_content.php?delete=<?php echo htmlspecialchars($row['id']); ?>" onclick="return confirm('¿Estás seguro de eliminar este contenido?');">Eliminar</a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else : ?>
                <p>No se encontró contenido.</p>
            <?php endif; ?>
        </section>
    </div>
</body>
</html>