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
const userName = document.getElementById('userName');
const logoutBtn = document.getElementById('logoutBtn');

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Authentication state observer
    auth.onAuthStateChanged((user) => {
        if (user) {
            // Get user data from Firestore
            const userRef = firebase.firestore().collection('users').doc(user.uid);
            userRef.get().then((doc) => {
                if (doc.exists()) {
                    const data = doc.data();
                    // Update welcome message with nickname or email
                    userName.textContent = `Welcome, ${data.nickname || user.email}!`;
                } else {
                    userName.textContent = `Welcome, ${user.email}!`;
                }
            }).catch((error) => {
                console.error('Error loading user data:', error);
                userName.textContent = `Welcome, ${user.email}!`;
            });
        } else {
            window.location.href = '/login';
        }
    });

    // Logout handler
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            auth.signOut()
                .then(() => {
                    window.location.href = '/login';
                })
                .catch((error) => {
                    console.error('Logout error:', error);
                });
        });
    }
}); 