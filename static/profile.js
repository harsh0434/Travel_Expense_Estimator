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
const db = firebase.firestore();

// DOM Elements
const userName = document.getElementById('userName');
const userEmail = document.getElementById('userEmail');
const userAvatar = document.getElementById('userAvatar');
const userNickname = document.getElementById('userNickname');
const memberSince = document.getElementById('memberSince');
const totalTrips = document.getElementById('totalTrips');
const totalExpenses = document.getElementById('totalExpenses');
const logoutBtn = document.getElementById('logoutBtn');

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication state
    auth.onAuthStateChanged((user) => {
        if (user) {
            // User is signed in, update the UI
            updateProfileUI(user);
            loadUserData(user);
        } else {
            // No user is signed in, redirect to login
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

// Update profile UI with user data
function updateProfileUI(user) {
    if (userName) userName.textContent = user.displayName || 'User';
    if (userEmail) userEmail.textContent = user.email;
    if (userAvatar) {
        userAvatar.src = user.photoURL || 'https://via.placeholder.com/150';
    }
}

// Load user data from Firestore
async function loadUserData(user) {
    try {
        const userRef = db.collection('users').doc(user.uid);
        const doc = await userRef.get();
        
        if (doc.exists) {
            const data = doc.data();
            
            // Update profile information
            if (userNickname) userNickname.textContent = data.nickname || 'Not set';
            if (memberSince) {
                const date = user.metadata.creationTime;
                memberSince.textContent = new Date(date).toLocaleDateString();
            }
            
            // Update travel statistics
            if (totalTrips) totalTrips.textContent = data.totalTrips || 0;
            if (totalExpenses) {
                const expenses = data.totalExpenses || 0;
                totalExpenses.textContent = `$${expenses.toLocaleString()}`;
            }
        }
    } catch (error) {
        console.error('Error loading user data:', error);
    }
} 