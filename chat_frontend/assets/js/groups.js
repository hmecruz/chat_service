import socket from './socket.js'; // ✅ Must be at the top for ES modules

document.addEventListener('DOMContentLoaded', () => {
    const groups = [];
    const groupList = document.getElementById('group-list');
    const createGroupBtn = document.getElementById('create-group-btn');
    const createGroupModal = document.getElementById('create-group-modal');
    const cancelBtn = document.getElementById('cancel-btn');
    const createGroupForm = document.getElementById('create-group-form');
    const groupNameInput = document.getElementById('group-name');
    const usersInput = document.getElementById('users');

    // Shared state
    window.groupsData = {
        groups,
        currentGroupId: null,
        currentPage: 1, // Track the current page
        isLoading: false, // Flag to prevent multiple requests while loading
    };

    // Function to render groups to the UI
    window.renderGroups = function (groups) {
        groupList.innerHTML = ''; // Clear the list for the initial render
        groups.forEach(group => {
            const li = document.createElement('li');
            li.className = "flex items-center gap-3 p-3 bg-gray-100 rounded-lg hover:bg-green-100 cursor-pointer transition";

            li.innerHTML = `
                <div class="text-2xl">${group.image || '📦'}</div>
                <div class="font-medium text-gray-800">${group.groupName || group.name}</div>
            `;
            li.addEventListener('click', () => {
                window.groupsData.currentGroupId = group.chatId || group.id;
                console.log('groups.js: currentGroupId set to:', window.groupsData.currentGroupId, 'after group click');
                window.showChatUI(group); // From chat.js
                console.log('groups.js: showChatUI function called with group:', group);
            });

            groupList.appendChild(li);
        });
    };

    window.renderGroups(groups); // Initial render

    // Function to fetch the chat groups
    function fetchChatGroups() {
        if (window.groupsData.isLoading) return; // Prevent multiple requests while loading
        window.groupsData.isLoading = true; // Set loading flag

        // Emit the event to get groups, passing the current page
        const userId = localStorage.getItem('userId'); // Assuming userId is saved in localStorage
        if (!userId) {
            alert("User is not logged in. Please log in.");
            window.groupsData.isLoading = false;
            return;
        }

        socket.emit('user/chats', {
            userId,
            page: window.groupsData.currentPage,
            limit: 20
        });
    }

    // Fetch chat groups when the page loads
    fetchChatGroups();

    // Handle scrolling to the bottom
    groupList.addEventListener('scroll', () => {
        if (groupList.scrollTop + groupList.clientHeight >= groupList.scrollHeight) {
            // User has scrolled to the bottom, load more groups
            window.groupsData.currentPage += 1; // Increase the page number
            fetchChatGroups(); // Fetch more groups
        }
    });

    createGroupBtn.addEventListener('click', () => {
        createGroupModal.classList.remove('hidden');
    });

    cancelBtn.addEventListener('click', () => {
        createGroupModal.classList.add('hidden');
        createGroupForm.reset();
    });

    createGroupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const groupName = groupNameInput.value.trim();
        let users = usersInput.value.trim().split(',').map(user => user.trim());

        if (!groupName || users.length < 1) {  // We require at least 1 user (including the creator)
            alert("Please provide a group name and at least 1 user.");
            return;
        }

        // Retrieve the logged-in user ID from localStorage (replace with actual logic if needed)
        const loggedInUserId = localStorage.getItem('userId'); // Assuming userId is saved in localStorage

        if (!loggedInUserId) {
            alert("User is not logged in. Please log in.");
            return;
        }

        // Add the logged-in user to the users list if it's not already included
        if (!users.includes(loggedInUserId)) {
            users.unshift(loggedInUserId);  // Add logged-in user as the first element
        }

        const payload = {
            groupName,
            users
        };

        // Emit event to backend
        socket.emit('chat/create', payload);
    });

    // Handle successful group creation
    socket.on('chatGroupCreated', (data) => {
        const newGroup = {
            chatId: data.chatId,
            groupName: data.groupName,
            users: data.users,
            createdAt: data.createdAt,
            image: "📦"
        };

        // Ensure the new group doesn't already exist before adding it
        const existingGroup = window.groupsData.groups.find(group => group.chatId === newGroup.chatId);
        if (!existingGroup) {
            // Add the new group to the beginning of the list (most recent first)
            window.groupsData.groups.unshift(newGroup);
            window.renderGroups(window.groupsData.groups); // Re-render with updated group list
        }

        createGroupModal.classList.add('hidden');
        createGroupForm.reset();
    });

    // Handle group creation error
    socket.on('creation_error', (errorMsg) => {
        alert("Error creating chat group: " + errorMsg);
    });

    // Handle the chat list response from the server
    socket.on('getUserChats', (data) => {
        if (data && data.chats) {
            // Filter out groups that are already in the list before adding
            const newGroups = data.chats.filter(group => !window.groupsData.groups.some(existingGroup => existingGroup.chatId === group.chatId));
            window.groupsData.groups = window.groupsData.groups.concat(newGroups);
            window.renderGroups(window.groupsData.groups); // Re-render with updated groups
            window.groupsData.isLoading = false; // Reset the loading flag
        } else {
            alert("Failed to load chats.");
            window.groupsData.isLoading = false;
        }
    });
});

console.log('groups.js finished loading');
