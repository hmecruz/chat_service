// chat.js
const socket = io("http://localhost:5000", { transports: ["websocket"] });

const sendBtn = document.getElementById("send-btn");
const input = document.getElementById("message-input");
const messagesContainer = document.getElementById("messages");

const currentUser = "user1"; // Replace with the actual user
const currentChatId = "chat123"; // Replace dynamically per chat

sendBtn.addEventListener("click", () => {
  const content = input.value.trim();
  if (content) {
    socket.emit("sendMessage", {
      chatId: currentChatId,
      senderId: currentUser,
      content: content,
    });
    input.value = "";
  }
});

socket.on("receiveMessage", (data) => {
  data.messages.forEach((msg) => {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message");
    if (msg.senderId === currentUser) {
      msgDiv.classList.add("you");
    }
    msgDiv.innerText = msg.content;
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  });
});
