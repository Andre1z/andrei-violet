document.addEventListener("DOMContentLoaded", function() {
    // Variables ya definidas previamente...
    const btnHide = document.getElementById("btn-hide");
    const btnShow = document.getElementById("btn-show");
    const sidebar = document.getElementById("sidebar");
    const chatArea = document.getElementById("chat-area");
    const btnNewChat = document.getElementById("btn-new-chat");
    const sessionList = document.getElementById("chat-session-list");
    const btnOptions = document.getElementById("btn-options");
    const popupOptions = document.getElementById("popup-options");
    const btnDeleteChat = document.getElementById("btn-delete-chat");
    const btnShareChat = document.getElementById("btn-share-chat");
    const btnClosePopup = document.getElementById("btn-close-popup");
    let currentChatId = null; // Identificador de la sesión en curso

    // Ocultar el sidebar y mostrar el botón "btn-show"
    btnHide.addEventListener("click", function() {
        sidebar.classList.add("hidden");
        chatArea.classList.add("full");
        btnShow.style.display = "block";
    });

    // Mostrar el sidebar cuando se pulsa el botón "btn-show"
    btnShow.addEventListener("click", function() {
        sidebar.classList.remove("hidden");
        chatArea.classList.remove("full");
        btnShow.style.display = "none";
    });

    // Crear una nueva sesión de chat
    btnNewChat.addEventListener("click", function() {
        fetch("new_chat.php", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.chat_id) {
                currentChatId = data.chat_id;
                document.getElementById("chat-messages").innerHTML = "";
                let newSessionDiv = document.createElement("div");
                newSessionDiv.classList.add("chat-session");
                newSessionDiv.dataset.chatId = data.chat_id;
                let now = new Date();
                newSessionDiv.innerHTML = "Chat " + data.chat_id + "<br>" + now.toLocaleString();
                sessionList.prepend(newSessionDiv);
            }
        })
        .catch(error => console.error("Error al crear nuevo chat:", error));
    });

    // Cargar la conversación al pulsar una sesión en el sidebar
    sessionList.addEventListener("click", function(e) {
        let target = e.target;
        while (target && !target.classList.contains("chat-session")) {
            target = target.parentElement;
        }
        if (target) {
            let chatId = target.dataset.chatId;
            currentChatId = chatId;
            document.querySelectorAll(".chat-session").forEach(function(el) {
                el.classList.remove("active");
            });
            target.classList.add("active");
            fetch("load_chat.php?chat_id=" + chatId)
            .then(response => response.json())
            .then(data => {
                let chatMessages = document.getElementById("chat-messages");
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
    
    // Envío del formulario para enviar mensajes
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

    // Función para agregar mensajes y ajustar el scroll
    function appendMessage(sender, text) {
        const chatMessages = document.getElementById("chat-messages");
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Mostrar el modal de opciones al pulsar el botón de opciones (···)
    btnOptions.addEventListener("click", function() {
        popupOptions.style.display = "block";
    });

    // Cerrar el modal
    btnClosePopup.addEventListener("click", function() {
        popupOptions.style.display = "none";
    });
    
    // Acción para eliminar el chat
    btnDeleteChat.addEventListener("click", function() {
        if (currentChatId) {
            // Aquí puedes realizar una petición AJAX a un endpoint delete_chat.php
            // Por ejemplo:
            fetch("delete_chat.php", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chat_id: currentChatId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Si se eliminó correctamente, limpiar mensajes y quitar de la lista
                    document.getElementById("chat-messages").innerHTML = "";
                    const el = document.querySelector(`.chat-session[data-chat-id="${currentChatId}"]`);
                    if (el) el.remove();
                    currentChatId = null;
                    alert("Chat eliminado.");
                } else {
                    alert("Error al eliminar el chat: " + data.error);
                }
                popupOptions.style.display = "none";
            })
            .catch(error => {
                console.error("Error eliminando el chat:", error);
                popupOptions.style.display = "none";
            });
        }
    });
    
    // Acción para compartir el chat
    btnShareChat.addEventListener("click", function() {
        if (currentChatId) {
            // Por ejemplo, copiar la URL actual con el chat_id (puedes ajustar la lógica)
            const shareText = "Chat ID: " + currentChatId;
            // Usamos la API del portapapeles si está disponible
            if (navigator.clipboard) {
                navigator.clipboard.writeText(shareText)
                .then(() => alert("Chat compartido (texto copiado al portapapeles)."))
                .catch(err => alert("Error al copiar: " + err));
            } else {
                alert("Chat: " + shareText);
            }
        }
        popupOptions.style.display = "none";
    });
});