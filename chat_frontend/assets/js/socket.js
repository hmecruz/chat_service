// chat frontend script (e.g., index.js or chat.js)

// Get nickname from URL
const urlParams = new URLSearchParams(window.location.search);
let nickname = urlParams.get('nickname');

if (!nickname) {
    console.log('No nickname found in URL, defaulting to guest.');
    nickname = 'user1'; // fallback
}

console.log("Got nickname:", nickname);
localStorage.setItem('userId', nickname);

// auth
const Auth = () => {
    const userId = nickname;
    localStorage.setItem('userId', userId);
    console.log('Authentication simulated: ', { userId });
};

Auth();

// Use it to connect via Socket.IO
const userId = localStorage.getItem('userId');

if (!userId) {
    window.location.href = '/login'; // This should never happen 
}

const socket = io({
    auth: {
        userId: userId
    },
    extraHeaders: {
        'userId': userId
    }
});

export default socket;
