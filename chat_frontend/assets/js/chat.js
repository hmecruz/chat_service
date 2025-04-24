document.addEventListener('DOMContentLoaded', () => {
    const chatHeader = document.getElementById('chat-header');
    const chatMessages = document.getElementById('chat-messages');
    const chatInputContainer = document.getElementById('chat-input-container');
    const chatInput = document.getElementById('chat-input');
    const sendMessageBtn = document.getElementById('send-message-btn');

    const currentUser = "You";
    const messagesByGroupId = {};
    let activeControlsIndex = null;
    let currentActiveGroup = null;
    let editGroupModal, editGroupNameInput, editUsersInput, editCancelBtn, editConfirmBtn, editGroupFormElement;

    const createEditGroupModal = () => {
        editGroupModal = document.createElement('div');
        editGroupModal.id = 'edit-group-modal';
        editGroupModal.className = 'fixed inset-0 flex justify-center items-center bg-gray-900 bg-opacity-50 hidden';
        editGroupModal.innerHTML = `
            <div class="bg-white p-6 rounded-lg shadow-lg w-96">
                <h2 class="text-xl font-semibold mb-4">Edit Group</h2>
                <form id="edit-group-form">
                    <div class="mb-4">
                        <label for="edit-group-name" class="block text-gray-700">Group Name</label>
                        <input type="text" id="edit-group-name" name="edit-group-name" class="w-full px-4 py-2 border rounded-lg" required />
                    </div>
                    <div class="mb-4">
                        <label for="edit-users" class="block text-gray-700">Users (comma separated)</label>
                        <input type="text" id="edit-users" name="edit-users" class="w-full px-4 py-2 border rounded-lg" required />
                        <p class="text-sm text-gray-500 mt-1">Separate users with commas.</p>
                    </div>
                    <div class="flex justify-between">
                        <button type="button" id="edit-cancel-btn" class="bg-gray-300 text-white px-4 py-2 rounded-lg">Cancel</button>
                        <button type="submit" id="edit-confirm-btn" class="bg-blue-500 text-white px-4 py-2 rounded-lg">Update</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(editGroupModal);

        editGroupFormElement = document.getElementById('edit-group-form');
        editGroupNameInput = document.getElementById('edit-group-name');
        editUsersInput = document.getElementById('edit-users');
        editCancelBtn = document.getElementById('edit-cancel-btn');
        editConfirmBtn = document.getElementById('edit-confirm-btn');

        editCancelBtn.addEventListener('click', () => {
            editGroupModal.classList.add('hidden');
        });

        editConfirmBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentActiveGroup && window.groupsData && window.groupsData.groups) { // Ensure window.groupsData and its groups property exist
                const newGroupName = editGroupNameInput.value.trim();
                const newUsers = editUsersInput.value.trim().split(',').map(user => user.trim());

                if (newGroupName) {
                    const groupIndex = window.groupsData.groups.findIndex(g => g.id === currentActiveGroup.id);
                    if (groupIndex !== -1) {
                        window.groupsData.groups[groupIndex].name = newGroupName;
                        window.groupsData.groups[groupIndex].users = newUsers;
                        window.renderGroups(window.groupsData.groups);
                        editGroupModal.classList.add('hidden');
                        chatHeader.innerHTML = `
                            ${newGroupName}
                            <button id="edit-group-header-btn" class="text-gray-500 hover:text-blue-500 focus:outline-none ml-2">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536-7.072 7.072m1.414-1.414l7.071-7.071 7.07 7.071a4 4 0 01-5.656 5.656l-7.07-7.071 1.414-1.414z" />
                                </svg>
                            </button>
                        `;
                        const newEditGroupHeaderBtn = document.getElementById('edit-group-header-btn');
                        if (newEditGroupHeaderBtn) {
                            newEditGroupHeaderBtn.addEventListener('click', () => {
                                if (currentActiveGroup) {
                                    editGroupNameInput.value = currentActiveGroup.name;
                                    editUsersInput.value = currentActiveGroup.users ? currentActiveGroup.users.join(', ') : '';
                                    editGroupModal.classList.remove('hidden');
                                }
                            });
                        }
                    } else {
                        alert("Error: Active group not found in the group list.");
                    }
                } else {
                    alert("Please provide a group name.");
                }
            } else {
                console.error("Error: window.groupsData or window.groupsData.groups is not initialized.");
                alert("An error occurred while updating the group.");
            }
        });

        editGroupFormElement.addEventListener('submit', (e) => {
            e.preventDefault();
        });
    };

    createEditGroupModal();

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

        currentActiveGroup = group; // Store the active group

        chatHeader.innerHTML = `
            ${group.name}
            <button id="edit-group-header-btn" class="text-gray-500 hover:text-blue-500 focus:outline-none ml-2">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536-7.072 7.072m1.414-1.414l7.071-7.071 7.07 7.071a4 4 0 01-5.656 5.656l-7.07-7.071 1.414-1.414z" />
                </svg>
            </button>
        `;
        const editGroupHeaderBtn = document.getElementById('edit-group-header-btn');
        if (editGroupHeaderBtn) {
            editGroupHeaderBtn.addEventListener('click', () => {
                if (currentActiveGroup) {
                    editGroupNameInput.value = currentActiveGroup.name;
                    editUsersInput.value = currentActiveGroup.users ? currentActiveGroup.users.join(', ') : '';
                    editGroupModal.classList.remove('hidden');
                }
            });
        }

        preloadMessages(group.id);
        window.groupsData = window.groupsData || {}; // Ensure window.groupsData exists
        window.groupsData.currentGroupId = group.id;
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