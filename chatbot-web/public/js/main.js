document.addEventListener("DOMContentLoaded", function() {
    const btnHide = document.getElementById("btn-hide");
    const sidebar = document.getElementById("sidebar");
    const chatArea = document.getElementById("chat-area");
    const btnNewChat = document.getElementById("btn-new-chat");
    const sessionList = document.getElementById("chat-session-list");
    let currentChatId = null; // Identificador de la sesión actual

    // Función para ocultar/mostrar el sidebar
    btnHide.addEventListener("click", function() {
        sidebar.classList.toggle("hidden");
        chatArea.classList.toggle("full");
    });

    // Crear una nueva sesión de chat
    btnNewChat.addEventListener("click", function() {
        fetch("new_chat.php", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.chat_id) {
                currentChatId = data.chat_id;
                // Reinicia el área de mensajes para el nuevo chat
                document.getElementById("chat-messages").innerHTML = "";
                // Insertar la nueva sesión en la lista (al principio)
                let newSessionDiv = document.createElement("div");
                newSessionDiv.classList.add("chat-session");
                newSessionDiv.dataset.chatId = data.chat_id;
                let now = new Date();
                newSessionDiv.innerHTML = "Chat " + data.chat_id + "<br>" + now.toLocaleString();
                sessionList.prepend(newSessionDiv);
            }
        })
        .catch(error => {
            console.error("Error al crear nuevo chat:", error);
        });
    });

    // Cargar la conversación de una sesión al hacer clic en ella
    sessionList.addEventListener("click", function(e) {
        let target = e.target;
        // Asegurarse de obtener el elemento con la clase "chat-session"
        while (target && !target.classList.contains("chat-session")) {
            target = target.parentElement;
        }
        if (target) {
            let chatId = target.dataset.chatId;
            currentChatId = chatId;

            // Resaltar la sesión seleccionada
            document.querySelectorAll(".chat-session").forEach(function(el) {
                el.classList.remove("active");
            });
            target.classList.add("active");

            // Solicitar la conversación mediante AJAX a load_chat.php
            fetch("load_chat.php?chat_id=" + chatId)
            .then(response => response.json())
            .then(data => {
                const chatMessages = document.getElementById("chat-messages");
                chatMessages.innerHTML = "";
                if (Array.isArray(data.messages)) {
                    data.messages.forEach(function(message) {
                        let msgDiv = document.createElement("div");
                        msgDiv.classList.add("message", message.sender);
                        msgDiv.textContent = message.message;
                        chatMessages.appendChild(msgDiv);
                    });
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            })
            .catch(error => console.error("Error al cargar chat:", error));
        }
    });

    // Envío del formulario para enviar mensajes (incluyendo chat_id)
    document.getElementById("chat-form").addEventListener("submit", function(e) {
        e.preventDefault();
        const messageInput = document.getElementById("message");
        const message = messageInput.value.trim();
        if (message === "") return;
        
        appendMessage("user", message);

        let formData = new FormData();
        formData.append("message", message);
        formData.append("chat_id", currentChatId);

        fetch("chat_process.php", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.reply) {
                appendMessage("bot", data.reply);
            }
        })
        .catch(error => console.error("Error procesando el mensaje:", error));

        messageInput.value = "";
    });

    // Función para agregar mensajes en la interfaz y desplazar el scroll hacia abajo
    function appendMessage(sender, text) {
        const chatMessages = document.getElementById("chat-messages");
        let messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});