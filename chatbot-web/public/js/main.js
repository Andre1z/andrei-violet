document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message");
  const chatMessages = document.getElementById("chat-messages");

  // Función para agregar un mensaje al área de mensajes
  function appendMessage(sender, text) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender); // Agrega clases para estilos (ej.: 'user' ó 'bot')
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    // Mover scroll hasta el final para ver el mensaje recién añadido
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Intercepta el envío del formulario
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message === "") return;

    // Agrega el mensaje del usuario en el área de mensajes
    appendMessage("user", message);

    // Prepara los datos a enviar en formato FormData
    const formData = new FormData();
    formData.append("message", message);

    // Envía la petición al servidor
    fetch("chat_process.php", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Se espera que 'data.reply' contenga la respuesta del chatbot
        if (data.reply) {
          appendMessage("bot", data.reply);
        }
      })
      .catch((error) => {
        console.error("Error enviando el mensaje:", error);
      });

    // Limpia el campo de mensaje después de enviar
    messageInput.value = "";
  });
});