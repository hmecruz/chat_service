// Simulate a successful login/authentication and store the userId for testing
const simulateAuth = () => {
    // Simulating the login/authentication process
    const userId = 'user1'; // Use a mock userId for testing purposes
    
    // Store the userId in localStorage
    localStorage.setItem('userId', userId); // Store userId in localStorage
    
    console.log('Authentication simulated: ', { userId });
};

// Call simulateAuth once to simulate the login process
simulateAuth();

// Now, get the userId from localStorage to pass into the Socket.IO connection
const userId = localStorage.getItem('userId');

// If no userId is found, redirect to login page or handle accordingly
if (!userId) {
    window.location.href = '/login'; // Example: redirect to login page
}

const socket = io({
    auth: {
        userId: userId // Pass userId directly for authentication
    },
    extraHeaders: {
        'userId': userId // Pass userId as a header if necessary
    }
});

export default socket;
