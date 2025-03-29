// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyD-KNs5W-18FF60nVhncJD0lyD8BAC03w4",
    authDomain: "travel-expense-e160e.firebaseapp.com",
    projectId: "travel-expense-e160e",
    storageBucket: "travel-expense-e160e.firebasestorage.app",
    messagingSenderId: "193251517541",
    appId: "1:193251517541:web:90653d68d54c2c68c1128c"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// DOM Elements
const userEmail = document.getElementById('user-email');
const logoutBtn = document.getElementById('logout-btn');

// Authentication State Observer
auth.onAuthStateChanged((user) => {
    if (user) {
        if (user.emailVerified) {
            userEmail.textContent = user.email;
        } else {
            window.location.href = '/login';
        }
    } else {
        window.location.href = '/login';
    }
});

// Logout Function
logoutBtn.addEventListener('click', async () => {
    try {
        await auth.signOut();
        window.location.href = '/login';
    } catch (error) {
        console.error('Error signing out:', error);
        alert('Error signing out. Please try again.');
    }
}); 