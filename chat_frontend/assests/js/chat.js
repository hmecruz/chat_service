document.addEventListener('DOMContentLoaded', () => {
    const chatHeader = document.getElementById('chat-header');
    const chatMessages = document.getElementById('chat-messages');
    const chatInputContainer = document.getElementById('chat-input-container');
    const chatInput = document.getElementById('chat-input');
    const sendMessageBtn = document.getElementById('send-message-btn');

    const currentUser = "You";  // Replace with actual username in future
    const messagesByGroupId = {};

    let activeControlsIndex = null; // Track which message has the active control panel

    // Preload fake messages for testing
    function preloadMessages(groupId) {
        if (!messagesByGroupId[groupId]) {
            messagesByGroupId[groupId] = [
                { sender: "Alice", text: "Hey there! 👋", timestamp: "10:01 AM" },
                { sender: "Bob", text: "Hi! Ready for the meeting?", timestamp: "10:02 AM" }
            ];
        }
    }

    window.showChatUI = function (group) {
        chatHeader.classList.remove('hidden');
        chatMessages.classList.remove('hidden');
        chatInputContainer.classList.remove('hidden');

        chatHeader.textContent = group.name;

        preloadMessages(group.id);
        window.groupsData = { currentGroupId: group.id };
        renderMessages(group.id);
    };

    function renderMessages(groupId) {
        const messages = messagesByGroupId[groupId] || [];
        chatMessages.innerHTML = ''; // Reset chat messages

        messages.forEach((msg, index) => {
            const isCurrentUser = msg.sender === currentUser;

            const wrapper = document.createElement('div');
            wrapper.className = "relative flex flex-col mb-2";

            const msgDiv = document.createElement('div');
            msgDiv.className = `
                max-w-[75%] p-3 rounded-lg shadow
                ${isCurrentUser ? 'bg-green-100 self-end text-right' : 'bg-white self-start text-left'}
                cursor-pointer
            `;

            msgDiv.innerHTML = `
                <div class="text-sm font-semibold text-gray-700">${msg.sender}</div>
                <div class="text-base text-gray-900 break-words" data-msg-text>${msg.text}</div>
                <div class="text-xs text-gray-400 mt-1">${msg.timestamp}</div>
            `;

            // Only allow controls for current user's messages
            if (isCurrentUser) {
                msgDiv.addEventListener('click', () => {
                    activeControlsIndex = activeControlsIndex === index ? null : index;
                    renderMessages(groupId);  // Re-render to toggle control panel visibility
                });
            }

            // Append message bubble
            wrapper.appendChild(msgDiv);

            // Create and append controls only if the message is clicked
            if (isCurrentUser && activeControlsIndex === index) {
                const controls = createControlBox(isCurrentUser, index);
                wrapper.appendChild(controls);
            }

            chatMessages.appendChild(wrapper);
        });

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Helper function to create edit/delete controls box
    function createControlBox(isCurrentUser, index) {
        const controls = document.createElement('div');
        controls.className = `
            absolute bottom-[-30px] ${isCurrentUser ? 'right-0' : 'left-0'}
            flex ${isCurrentUser ? 'justify-end' : 'justify-start'} gap-2 px-2 py-1 bg-gray-100 border border-gray-300 rounded-md
            text-sm text-gray-700 shadow-sm w-auto z-10
        `;

        const editBtn = document.createElement('button');
        editBtn.innerHTML = `<span role="img" aria-label="edit">✏️</span> Edit`;
        editBtn.onclick = () => handleEditMessage(index);

        const deleteBtn = document.createElement('button');
        deleteBtn.innerHTML = `<span role="img" aria-label="delete">🗑️</span> Delete`;
        deleteBtn.onclick = () => handleDeleteMessage(index);

        controls.appendChild(editBtn);
        controls.appendChild(deleteBtn);
        return controls;
    }

    function handleDeleteMessage(index) {
        if (confirm("Are you sure you want to delete this message?")) {
            const currentGroupId = window.groupsData?.currentGroupId;
            messagesByGroupId[currentGroupId].splice(index, 1);
            activeControlsIndex = null;
            renderMessages(currentGroupId);
        }
    }

    function handleEditMessage(index) {
        const currentGroupId = window.groupsData?.currentGroupId;
        const message = messagesByGroupId[currentGroupId][index];
        const newText = prompt("Edit your message:", message.text);

        if (newText !== null && newText.trim() !== "") {
            message.text = newText.trim();
            renderMessages(currentGroupId);
        }
    }

    function addMessageToGroup(groupId, sender, text) {
        if (!messagesByGroupId[groupId]) messagesByGroupId[groupId] = [];

        messagesByGroupId[groupId].push({
            sender,
            text,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
    }

    sendMessageBtn.addEventListener('click', () => {
        const message = chatInput.value.trim();
        const currentGroupId = window.groupsData?.currentGroupId;

        if (message && currentGroupId !== null) {
            addMessageToGroup(currentGroupId, currentUser, message);
            chatInput.value = '';
            activeControlsIndex = null;
            renderMessages(currentGroupId);
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessageBtn.click();
        }
    });
});
