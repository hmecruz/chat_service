document.addEventListener('DOMContentLoaded', () => {
    const groups = [
        { id: 1, name: "Family", image: "👨‍👩‍👧‍👦" },
        { id: 2, name: "Friends", image: "🧑‍🤝‍🧑" },
        { id: 3, name: "Work", image: "💼" },
        { id: 4, name: "Gaming", image: "🎮" }
    ];

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
    };

    // Make renderGroups accessible globally
    window.renderGroups = function (groups) {
        groupList.innerHTML = '';
        groups.forEach(group => {
            const li = document.createElement('li');
            li.className = "flex items-center gap-3 p-3 bg-gray-100 rounded-lg hover:bg-green-100 cursor-pointer transition";

            li.innerHTML = `
                <div class="text-2xl">${group.image}</div>
                <div class="font-medium text-gray-800">${group.name}</div>
            `;
            li.addEventListener('click', () => {
                window.groupsData.currentGroupId = group.id;
                window.showChatUI(group);  // From chat.js
            });

            groupList.appendChild(li);
        });
    };

    window.renderGroups(groups); // Initial rendering

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
        const users = usersInput.value.trim().split(',').map(user => user.trim());

        if (groupName && users.length > 0) {
            const newGroup = {
                id: groups.length + 1,
                name: groupName,
                image: "📦",
                users: users
            };

            groups.push(newGroup);
            window.renderGroups(groups); // Use the global renderGroups
            createGroupModal.classList.add('hidden');
            createGroupForm.reset();
        } else {
            alert("Please provide both group name and users.");
        }
    });
});