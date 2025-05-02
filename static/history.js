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
const historyList = document.getElementById('historyList');
const sortBy = document.getElementById('sortBy');
const searchInput = document.getElementById('searchInput');
const logoutBtn = document.getElementById('logoutBtn');

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication state
    auth.onAuthStateChanged((user) => {
        if (user) {
            // User is signed in, load history
            loadHistory(user);
        } else {
            // No user is signed in, redirect to login
            window.location.href = '/login';
        }
    });

    // Add event listeners for sorting and searching
    sortBy.addEventListener('change', () => {
        const user = auth.currentUser;
        if (user) loadHistory(user);
    });

    searchInput.addEventListener('input', () => {
        const user = auth.currentUser;
        if (user) loadHistory(user);
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

// Load and display history
async function loadHistory(user) {
    try {
        const historyRef = db.collection('users').doc(user.uid).collection('history');
        let query = historyRef;

        // Apply sorting
        const sortValue = sortBy.value;
        switch (sortValue) {
            case 'date-desc':
                query = query.orderBy('timestamp', 'desc');
                break;
            case 'date-asc':
                query = query.orderBy('timestamp', 'asc');
                break;
            case 'cost-desc':
                query = query.orderBy('totalCost', 'desc');
                break;
            case 'cost-asc':
                query = query.orderBy('totalCost', 'asc');
                break;
        }

        const snapshot = await query.get();
        const searchTerm = searchInput.value.toLowerCase();

        // Clear existing history
        historyList.innerHTML = '';

        if (snapshot.empty) {
            historyList.innerHTML = '<div class="no-history">No travel history found</div>';
            return;
        }

        // Display history items
        snapshot.forEach(doc => {
            const data = doc.data();
            
            // Filter by search term if present
            if (searchTerm && !data.destination.toLowerCase().includes(searchTerm)) {
                return;
            }

            const historyItem = createHistoryItem(doc.id, data);
            historyList.appendChild(historyItem);
        });
    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = '<div class="error">Error loading history</div>';
    }
}

// Create a history item element
function createHistoryItem(id, data) {
    const item = document.createElement('div');
    item.className = 'history-item';
    
    const date = new Date(data.timestamp.toDate()).toLocaleDateString();
    const time = new Date(data.timestamp.toDate()).toLocaleTimeString();
    
    item.innerHTML = `
        <div class="history-item-header">
            <h3>${data.destination}</h3>
            <span class="history-date">${date} ${time}</span>
        </div>
        <div class="history-item-details">
            <div class="detail-row">
                <span class="label">Duration:</span>
                <span>${data.duration} days</span>
            </div>
            <div class="detail-row">
                <span class="label">Travelers:</span>
                <span>${data.travelers}</span>
            </div>
            <div class="detail-row">
                <span class="label">Total Cost:</span>
                <span class="cost">₹${data.totalCost.toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="label">Cost per Person:</span>
                <span>₹${(data.totalCost / data.travelers).toLocaleString()}</span>
            </div>
        </div>
    `;
    
    return item;
} 