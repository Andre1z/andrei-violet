document.addEventListener("DOMContentLoaded", function() {
    // Elementos del DOM
    const btnHide = document.getElementById("btn-hide");
    const btnShow = document.getElementById("btn-show");
    const sidebar = document.getElementById("sidebar");
    const chatArea = document.getElementById("chat-area");
    const btnNewChat = document.getElementById("btn-new-chat");
    const sessionList = document.getElementById("chat-session-list");
    const popupOptions = document.getElementById("popup-options");
    const btnDeleteChat = document.getElementById("btn-delete-chat");
    const btnShareChat = document.getElementById("btn-share-chat");
    const btnClosePopup = document.getElementById("btn-close-popup");
    const chatForm = document.getElementById("chat-form");
    const chatMessages = document.getElementById("chat-messages");

    let currentChatId = null; // Identificador de la sesión en curso

    /* ================================
       Mostrar/Ocultar Sidebar
       ================================ */
    btnHide.addEventListener("click", function() {
        sidebar.classList.add("hidden");
        chatArea.classList.add("full");
        btnShow.style.display = "block";
    });

    btnShow.addEventListener("click", function() {
        sidebar.classList.remove("hidden");
        chatArea.classList.remove("full");
        btnShow.style.display = "none";
    });

    /* ================================
       Crear Nueva Sesión de Chat
       ================================ */
    btnNewChat.addEventListener("click", function() {
        fetch("new_chat.php", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.chat_id) {
                    currentChatId = data.chat_id;
                    chatMessages.innerHTML = "";
                    // Crear el elemento del nuevo chat en la lista, con botón de opciones
                    let newSessionDiv = document.createElement("div");
                    newSessionDiv.classList.add("chat-session");
                    newSessionDiv.dataset.chatId = data.chat_id;
                    let now = new Date();
                    newSessionDiv.innerHTML = `
                        <div class="chat-session-info">
                          <span>Chat ${data.chat_id}</span>
                          <span>${now.toLocaleString()}</span>
                        </div>
                        <button class="chat-options" title="Opciones">···</button>
                    `;
                    sessionList.prepend(newSessionDiv);
                }
            })
            .catch(error => {
                console.error("Error al crear nuevo chat:", error);
            });
    });

    /* ================================
       Delegación de Eventos en la Lista de Chat Sessions
       ================================ */
    sessionList.addEventListener("click", function(e) {
        // Si se pulsa el botón de opciones de una sesión:
        if (e.target.classList.contains("chat-options")) {
            const parentSession = e.target.closest(".chat-session");
            if (parentSession) {
                currentChatId = parentSession.dataset.chatId;
                // Mostrar el modal de opciones
                popupOptions.style.display = "block";
            }
            return; // No se carga el chat si se pulso el botón de opciones
        }
        
        // Si se hace clic en otro lado de una sesión, se carga ese chat
        let target = e.target;
        while (target && !target.classList.contains("chat-session")) {
            target = target.parentElement;
        }
        if (target) {
            currentChatId = target.dataset.chatId;
            // Quitar clase "active" de todas las sesiones y marcar la seleccionada
            document.querySelectorAll(".chat-session").forEach(function(el) {
                el.classList.remove("active");
            });
            target.classList.add("active");
            // Cargar la conversación mediante AJAX
            fetch("load_chat.php?chat_id=" + currentChatId)
                .then(response => response.json())
                .then(data => {
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

    /* ================================
       Enviar Mensaje (Chat Form)
       ================================ */
    chatForm.addEventListener("submit", function(e) {
        e.preventDefault();
        const messageInput = document.getElementById("message");
        const message = messageInput.value.trim();
        if (message === "") return;
        // Mostrar el mensaje del usuario en la interfaz
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

    // Función para agregar mensajes y mantener el scroll actualizado
    function appendMessage(sender, text) {
        let msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender);
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /* ================================
       Modal - Opciones de Chat
       ================================ */
    btnClosePopup.addEventListener("click", function() {
        popupOptions.style.display = "none";
    });

    btnDeleteChat.addEventListener("click", function() {
        if (currentChatId) {
            fetch("delete_chat.php", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ chat_id: currentChatId })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Limpiar los mensajes y quitar el chat eliminado de la lista
                        chatMessages.innerHTML = "";
                        const sessionElem = document.querySelector(`.chat-session[data-chat-id="${currentChatId}"]`);
                        if (sessionElem) sessionElem.remove();
                        currentChatId = null;
                        alert("Chat eliminado exitosamente.");
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

    btnShareChat.addEventListener("click", function() {
        if (currentChatId) {
            const shareText = "Chat ID: " + currentChatId;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(shareText)
                    .then(() => alert("Información del chat copiada al portapapeles."))
                    .catch(err => alert("Error al copiar: " + err));
            } else {
                alert(shareText);
            }
        }
        popupOptions.style.display = "none";
    });
});