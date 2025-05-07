import socket from './socket.js';
import { updateChatName, addUsersToChat, removeUsersFromChat, deleteChat} from './api/chatGroupsAPI.js';
import { sendMessage, fetchMessageHistory, editMessage, deleteMessage} from './api/chatMessagesAPI.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatHeader = document.getElementById('chat-header');
    const chatMessages = document.getElementById('chat-messages');
    const chatInputContainer = document.getElementById('chat-input-container');
    const chatInput = document.getElementById('chat-input');
    const sendMessageBtn = document.getElementById('send-message-btn');

    const currentUser = "You";
    const messagesByGroupId = {};
    const renderedMessageIdsByGroup = {};
    
    let activeControlsIndex = null;
    let currentActiveGroup = null;
    let editGroupModal, editGroupNameInput, editUsersInput, editCancelBtn, editConfirmBtn, editGroupFormElement, deleteChatBtn, removeUsersInput;

    let currentChatGroupId;
    let currentChatGroupName;

    const messagesPerPage = 10;
    const messageHistoryState = {
        'undefined': { // Initialize with a default key, or null if preferred
            page: 1,
            isLoading: false,
            hasMore: true,
        }
    };

    const createEditGroupModal = () => {
        editGroupModal = document.createElement('div');
        editGroupModal.id = 'edit-group-modal';
        editGroupModal.className = 'fixed inset-0 flex justify-center items-center bg-gray-900 bg-opacity-50 hidden';
        editGroupModal.innerHTML = `
            <div class="bg-white p-8 rounded-xl shadow-md w-96">
                <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">Edit Group</h2>

                <form id="edit-group-form" class="space-y-6">
                    <div>
                        <label for="edit-group-name" class="block text-gray-700 text-sm font-bold mb-2">Group Name</label>
                        <input type="text" id="edit-group-name" name="edit-group-name" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" required />
                    </div>

                    <div>
                        <label for="edit-users" class="block text-gray-700 text-sm font-bold mb-2">Add Users (comma separated)</label>
                        <input type="text" id="edit-users" name="edit-users" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
                        <p class="text-gray-500 text-xs italic">Separate usernames with commas.</p>
                    </div>

                    <div>
                        <label for="remove-users" class="block text-gray-700 text-sm font-bold mb-2">Remove Users (comma separated)</label>
                        <input type="text" id="remove-users" name="remove-users" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" />
                        <p class="text-gray-500 text-xs italic">Separate usernames with commas.</p>
                    </div>

                    <div class="flex items-center justify-between mt-6">
                        <button type="button" id="edit-cancel-btn" class="bg-gray-400 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Cancel</button>
                        <button type="submit" id="edit-confirm-btn" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Update</button>
                    </div>
                </form>

                <div class="mt-8 pt-4 border-t border-gray-200 text-center">
                    <button id="delete-chat-btn" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">Delete Chat</button>
                </div>
            </div>
        `;
        document.body.appendChild(editGroupModal);
    
        editGroupFormElement = document.getElementById('edit-group-form');
        editGroupNameInput = document.getElementById('edit-group-name');
        editUsersInput = document.getElementById('edit-users');
        editCancelBtn = document.getElementById('edit-cancel-btn');
        editConfirmBtn = document.getElementById('edit-confirm-btn');
        deleteChatBtn = document.getElementById('delete-chat-btn');
        removeUsersInput = document.getElementById('remove-users');


        editCancelBtn.addEventListener('click', () => {
            editGroupModal.classList.add('hidden');
        });
    
        editConfirmBtn.addEventListener('click', (e) => {
            e.preventDefault();
        
            if (currentActiveGroup && window.groupsData && window.groupsData.groups) {
                const newGroupName = editGroupNameInput.value.trim();
                const usersToAdd = editUsersInput.value.trim().split(',').map(user => user.trim()).filter(Boolean);
                const usersToRemove = document.getElementById('remove-users').value.trim().split(',').map(user => user.trim()).filter(Boolean);
        
                if (newGroupName) {
                    const groupIndex = window.groupsData.groups.findIndex(g => g.id === currentActiveGroup.id);
                    if (groupIndex !== -1) {
                        const group = window.groupsData.groups[groupIndex];
        
                        // Only update name locally
                        group.name = newGroupName;
                        group.groupName = newGroupName;
        
                        // Emit updates
                        updateChatName(socket, currentChatGroupId, newGroupName);
                        if (usersToAdd.length > 0) addUsersToChat(socket, currentChatGroupId, usersToAdd);
                        if (usersToRemove.length > 0) removeUsersFromChat(socket, currentChatGroupId, usersToRemove);
        
                        window.renderGroups(window.groupsData.groups);
                        editGroupModal.classList.add('hidden');
        
                        // Update header with new name
                        chatHeader.innerHTML = `
                            ${newGroupName}
                            <button id="edit-group-header-btn" class="text-gray-500 hover:text-blue-500 focus:outline-none ml-2">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536-7.072 7.072m1.414-1.414l7.071-7.071 7.07 7.071a4 4 0 01-5.656 5.656l-7.07-7.071 1.414-1.414z" />
                                </svg>
                            </button>
                        `;
        
                        // Restore button functionality
                        const newEditGroupHeaderBtn = document.getElementById('edit-group-header-btn');
                        if (newEditGroupHeaderBtn) {
                            newEditGroupHeaderBtn.addEventListener('click', () => {
                                if (currentActiveGroup) {
                                    editGroupNameInput.value = currentActiveGroup.name;
                                    editUsersInput.value = '';
                                    document.getElementById('remove-users').value = '';
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

        deleteChatBtn.addEventListener('click', () => {
            if (currentActiveGroup && currentChatGroupId) {
                if (confirm("Are you sure you want to delete this chat group? This cannot be undone.")) {
                    console.log("Deleting chat group:", currentChatGroupId);
                    deleteChat(socket, currentChatGroupId);
                }
            } else {
                alert("No active group selected to delete.");
            }
        });
    };
    
    createEditGroupModal();

    // Listen for chat deletion success
    socket.on('chatGroupDeleted', (data) => {
        console.log('Group deleted:', data);

        if (data.deleted && data.chatId) {
            if (window.groupsData && window.groupsData.groups) {
                window.groupsData.groups = window.groupsData.groups.filter(group => group.id !== data.chatId && group.chatId !== data.chatId);
                window.renderGroups(window.groupsData.groups);
            }

            if (window.groupsData.currentGroupId === data.chatId) {
                window.groupsData.currentGroupId = null;
                window.clearChatUI && window.clearChatUI();
            }

            if (chatHeader) {
                chatHeader.innerHTML = '';
            }

            editGroupModal.classList.add('hidden');
        } else {
            alert("Failed to delete the group. Please try again.");
        }
    });

    socket.on('chatGroupNameUpdated', ({ chatId, newGroupName }) => {
        const group = window.groupsData.groups.find(g => g.id === chatId);
        if (group) {
            group.name = newGroupName;
        }
    
        if (window.groupsData.currentGroupId === chatId) {
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
        }
    
        window.renderGroups(window.groupsData.groups);
    });    

    function renderMessages(groupId, prepend = false) {
        if (!renderedMessageIdsByGroup[groupId]) {
            renderedMessageIdsByGroup[groupId] = new Set();
        }
    
        const renderedIds = renderedMessageIdsByGroup[groupId];
        const messages = messagesByGroupId[groupId] || [];
    
        if (!prepend) {
            chatMessages.innerHTML = ''; // 🔥 Clear previous content on fresh render
            renderedMessageIdsByGroup[groupId] = new Set(); // Reset rendered message tracking
        }
    
        const fragment = document.createDocumentFragment();
    
        messages.forEach((msg, index) => {
            if (renderedIds.has(msg.id) && !prepend) return;
            renderedIds.add(msg.id);
    
            const isCurrentUser = msg.sender === currentUser;
            const wrapper = document.createElement('div');
            wrapper.className = "relative flex flex-col mb-2";
    
            const msgDiv = document.createElement('div');
            msgDiv.className = `
                max-w-[75%] p-3 rounded-lg shadow
                ${isCurrentUser ? 'bg-green-100 self-end text-right' : 'bg-white self-start text-left'}
                cursor-pointer
            `.trim();
    
            msgDiv.innerHTML = `
                <div class="text-sm font-semibold text-gray-700">${msg.sender}</div>
                <div class="text-base text-gray-900 break-words" data-msg-text>
                    ${msg.text}
                    ${msg.edited ? '<span class="text-xs text-gray-400 ml-1">(edited)</span>' : ''}
                </div>
                <div class="text-xs text-gray-400 mt-1">${msg.timestamp}</div>
            `;
    
            // 👇 Toggle control panel on click
            if (isCurrentUser) {
                msgDiv.addEventListener('click', () => {
                    activeControlsIndex = (activeControlsIndex === index) ? null : index;
                    renderMessages(groupId);
                });
            }
    
            wrapper.appendChild(msgDiv);
    
            if (isCurrentUser && activeControlsIndex === index) {
                const controls = createControlBox(isCurrentUser, index);
                wrapper.appendChild(controls);
            }
    
            fragment.appendChild(wrapper);
        });
    
        if (prepend) {
            const currentScrollTop = chatMessages.scrollTop;
            chatMessages.prepend(fragment);
            chatMessages.scrollTop = currentScrollTop + fragment.scrollHeight;
        } else {
            chatMessages.appendChild(fragment);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Initialize the chat UI
    window.showChatUI = function (group) {
        chatHeader.classList.remove('hidden');
        chatMessages.classList.remove('hidden');
        chatInputContainer.classList.remove('hidden');

        currentActiveGroup = group;
        currentChatGroupId = group.chatId || group.id;
        currentChatGroupName = group.groupName || group.name;

        // ✅ Clear old messages from the UI
        chatMessages.innerHTML = '';
        renderedMessageIdsByGroup[currentChatGroupId] = new Set();

        // ✅ Ensure state is initialized for the new group
        messagesByGroupId[currentChatGroupId] = [];
        messageHistoryState[currentChatGroupId] = { page: 1, isLoading: false, hasMore: true };

        // Set up header with edit button
        chatHeader.innerHTML = `
            ${currentChatGroupName}
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
                    editGroupNameInput.value = currentChatGroupName;
                    editUsersInput.value = currentActiveGroup.users ? currentActiveGroup.users.join(', ') : '';
                    editGroupModal.classList.remove('hidden');
                }
            });
        }

        console.log('chat.js currentChatGroupId set to:', currentChatGroupId);

        // Initial empty render & fetch from server
        renderMessages(currentChatGroupId);
        loadInitialMessages(currentChatGroupId);
    };


    function loadInitialMessages(groupId) {
        if (!messageHistoryState[groupId].isLoading && messageHistoryState[groupId].hasMore) {
            messageHistoryState[groupId].isLoading = true;
            fetchMessageHistory(socket, groupId, messageHistoryState[groupId].page, messagesPerPage);
            console.log('Loading initial messages for group:', groupId);
        }
    }

    sendMessageBtn.addEventListener('click', () => {
        console.log('Send button clicked!');
        const currentGroupId = currentChatGroupId; // Use the local variable
        const senderId = localStorage.getItem('userId');

        const message = chatInput.value.trim();

        if (message && currentGroupId && senderId) {
            sendMessage(socket, currentGroupId, senderId, message);
            chatInput.value = '';
            activeControlsIndex = null;
        } else {
            console.log('Message not sent.');
            if (!message) console.log('  - Message is empty.');
            if (!currentGroupId) console.log('  - currentGroupId is null or undefined.');
            if (!senderId) console.log('  - senderId is null or undefined.');
        }
    });

    socket.on('receiveMessage', (data) => {
        console.log('Received message data:', data);
        if (data && data.chatId === currentChatGroupId) {
            const isHistoryLoad = data.page > 1;
            const newMessages = data.messages.map(msgData => ({
                id: msgData.messageId,
                sender: msgData.senderId === localStorage.getItem('userId') ? currentUser : msgData.senderId,
                text: msgData.content,
                timestamp: new Date(msgData.sentAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }));
    
            console.log(`Processing ${isHistoryLoad ? 'historical' : 'initial'} messages for page ${data.page}:`, newMessages);
    
            if (!messagesByGroupId[data.chatId]) {
                messagesByGroupId[data.chatId] = [];
            }
    
            if (isHistoryLoad) {
                if (isHistoryLoad) {
                    console.log('Before prepending:', messagesByGroupId[data.chatId].length);
                    messagesByGroupId[data.chatId] = [
                        ...newMessages.reverse(),
                        ...messagesByGroupId[data.chatId]
                    ];
                    console.log('After prepending:', messagesByGroupId[data.chatId].length);
                
                    // ✅ Only set to true if the server sent some messages
                    messageHistoryState[data.chatId].hasMore = data.messages.length > 0;
                }
            } else {
                console.log('Before initial load replace:', messagesByGroupId[data.chatId].length);
                messagesByGroupId[data.chatId] = [...newMessages];
                messagesByGroupId[data.chatId].reverse();
                console.log('After initial load replace and reverse:', messagesByGroupId[data.chatId].length);
            }

            if (!messageHistoryState[data.chatId]) {
                messageHistoryState[data.chatId] = {
                    isLoading: false,
                    hasMore: true
                };
            }
            
            messageHistoryState[data.chatId].isLoading = false;
            messageHistoryState[data.chatId].hasMore = isHistoryLoad
                ? data.messages.length > 0
                : data.messages.length < data.total;
    
            // ✅ Always reset loading state regardless of message type
            messageHistoryState[data.chatId].isLoading = false;
    
            renderMessages(data.chatId, isHistoryLoad);
        }
    });
    
    chatMessages.addEventListener('scroll', () => {
        console.log('Scroll event triggered');
        console.log('chatMessages.scrollTop:', chatMessages.scrollTop);
        console.log('currentChatGroupId:', currentChatGroupId);
        console.log('messageHistoryState[currentChatGroupId]?.hasMore:', messageHistoryState[currentChatGroupId]?.hasMore);
        console.log('messageHistoryState[currentChatGroupId]?.isLoading:', messageHistoryState[currentChatGroupId]?.isLoading);
        if (chatMessages.scrollTop === 0 && currentChatGroupId && messageHistoryState[currentChatGroupId]?.hasMore && !messageHistoryState[currentChatGroupId]?.isLoading) {
            messageHistoryState[currentChatGroupId].isLoading = true;
            messageHistoryState[currentChatGroupId].page++;
            fetchMessageHistory(socket, currentChatGroupId, messageHistoryState[currentChatGroupId].page, messagesPerPage);
            console.log('Fetching more messages...');
        }
    });


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

    function handleEditMessage(index) {
        const currentGroupId = window.groupsData?.currentGroupId;
        const message = messagesByGroupId[currentGroupId][index];
        const newText = prompt("Edit your message:", message.text);
    
        if (newText !== null && newText.trim() !== "" && newText !== message.text) {
            // Emit to server
            editMessage(socket, currentGroupId, message.id, newText.trim());
    
            // Optionally, optimistically update the UI
            message.text = newText.trim();
            renderMessages(currentGroupId);
        }
    }

    socket.on('messageEdited', (data) => {
        const { chatId, messageId, newContent, editedAt } = data;
        const messages = messagesByGroupId[chatId];
    
        if (messages) {
            const msg = messages.find(m => m.id === messageId);
            if (msg) {
                msg.text = newContent;
                msg.timestamp = new Date(editedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                renderMessages(chatId);
            }
        }
    });

    function handleDeleteMessage(index) {
        const currentGroupId = window.groupsData?.currentGroupId;
        const message = messagesByGroupId[currentGroupId][index];
    
        if (!message) return;
    
        if (confirm("Are you sure you want to delete this message?")) {
            deleteMessage(socket, currentGroupId, message.id); // 👈 Call the server
        }
    }

    socket.on('messageDeleted', ({ chatId, messageId }) => {
        const messages = messagesByGroupId[chatId];
        if (!messages) return;
    
        const index = messages.findIndex(m => m.id === messageId);
        if (index !== -1) {
            messages.splice(index, 1); // 🔥 remove it
            renderedMessageIdsByGroup[chatId]?.delete(messageId); // 🧽 clean up tracking
            if (window.groupsData?.currentGroupId === chatId) {
                activeControlsIndex = null;
                renderMessages(chatId); // ✅ re-render
            }
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessageBtn.click();
        }
    });
});

console.log('chat.js finished loading');