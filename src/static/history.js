// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyD-KNs5W-18FF60nVhncJD0lyD8BAC03w4",
    authDomain: "travel-expense-e160e.firebaseapp.com",
    projectId: "travel-expense-e160e",
    storageBucket: "travel-expense-e160e.appspot.com",
    messagingSenderId: "193251517541",
    appId: "1:193251517541:web:90653d68d54c2c68c1128c"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// DOM Elements
const historyContainer = document.getElementById('historyContainer');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const sortSelect = document.getElementById('sortSelect');
const clearHistoryBtn = document.getElementById('clearHistory');
const deleteModal = document.getElementById('deleteModal');
const confirmDeleteBtn = document.getElementById('confirmDelete');
const cancelDeleteBtn = document.getElementById('cancelDelete');
const logoutBtn = document.getElementById('logoutBtn');

let currentUser = null;
let currentHistory = [];
let selectedItemId = null;

// Check Authentication
auth.onAuthStateChanged(async (user) => {
    if (user) {
        currentUser = user;
        loadTravelHistory();
    } else {
        window.location.href = '/login';
    }
});

// Load Travel History
async function loadTravelHistory() {
    try {
        loadingState.style.display = 'block';
        historyContainer.style.display = 'none';
        emptyState.style.display = 'none';

        const snapshot = await db.collection('travel_history')
            .where('userId', '==', currentUser.uid)
            .orderBy('timestamp', 'desc')
            .get();

        currentHistory = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));

        if (currentHistory.length === 0) {
            showEmptyState();
        } else {
            renderHistory(currentHistory);
        }
    } catch (error) {
        console.error('Error loading history:', error);
        showError('Failed to load travel history');
    } finally {
        loadingState.style.display = 'none';
    }
}

// Render History Items
function renderHistory(history) {
    historyContainer.innerHTML = '';
    historyContainer.style.display = 'block';
    emptyState.style.display = 'none';

    history.forEach(item => {
        const date = new Date(item.timestamp.seconds * 1000);
        const formattedDate = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <div class="history-details">
                <h3>${item.destination}</h3>
                <div class="history-info">
                    <div class="info-item">
                        <i class="fas fa-calendar"></i>
                        <span>${formattedDate}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-users"></i>
                        <span>${item.people} People</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-clock"></i>
                        <span>${item.days} Days</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-rupee-sign"></i>
                        <span>₹${item.totalCost.toLocaleString()}</span>
                    </div>
                    <div class="info-item">
                        <i class="fas fa-tag"></i>
                        <span>${item.budgetLevel} Budget</span>
                    </div>
                </div>
            </div>
            <div class="history-actions">
                <button class="btn-icon" onclick="recalculate('${item.id}')">
                    <i class="fas fa-calculator"></i>
                </button>
                <button class="btn-icon delete" onclick="showDeleteModal('${item.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        historyContainer.appendChild(historyItem);
    });
}

// Show Empty State
function showEmptyState() {
    historyContainer.style.display = 'none';
    loadingState.style.display = 'none';
    emptyState.style.display = 'block';
}

// Filter and Sort
function filterAndSortHistory() {
    const searchTerm = searchInput.value.toLowerCase();
    const sortValue = sortSelect.value;

    let filteredHistory = currentHistory.filter(item =>
        item.destination.toLowerCase().includes(searchTerm)
    );

    switch (sortValue) {
        case 'date-desc':
            filteredHistory.sort((a, b) => b.timestamp.seconds - a.timestamp.seconds);
            break;
        case 'date-asc':
            filteredHistory.sort((a, b) => a.timestamp.seconds - b.timestamp.seconds);
            break;
        case 'cost-desc':
            filteredHistory.sort((a, b) => b.totalCost - a.totalCost);
            break;
        case 'cost-asc':
            filteredHistory.sort((a, b) => a.totalCost - b.totalCost);
            break;
    }

    renderHistory(filteredHistory);
}

// Delete Functions
function showDeleteModal(itemId) {
    selectedItemId = itemId;
    deleteModal.style.display = 'flex';
}

function hideDeleteModal() {
    deleteModal.style.display = 'none';
    selectedItemId = null;
}

async function deleteHistoryItem() {
    if (!selectedItemId) return;

    try {
        await db.collection('travel_history').doc(selectedItemId).delete();
        hideDeleteModal();
        loadTravelHistory();
    } catch (error) {
        console.error('Error deleting history item:', error);
        showError('Failed to delete history item');
    }
}

// Clear All History
async function clearAllHistory() {
    if (!confirm('Are you sure you want to clear all travel history? This action cannot be undone.')) {
        return;
    }

    try {
        const batch = db.batch();
        const snapshot = await db.collection('travel_history')
            .where('userId', '==', currentUser.uid)
            .get();

        snapshot.docs.forEach(doc => {
            batch.delete(doc.ref);
        });

        await batch.commit();
        loadTravelHistory();
    } catch (error) {
        console.error('Error clearing history:', error);
        showError('Failed to clear travel history');
    }
}

// Recalculate Function
function recalculate(itemId) {
    const historyItem = currentHistory.find(item => item.id === itemId);
    if (historyItem) {
        const queryParams = new URLSearchParams({
            destination: historyItem.destination,
            days: historyItem.days,
            people: historyItem.people,
            travel_mode: historyItem.travelMode,
            budget_level: historyItem.budgetLevel
        });
        window.location.href = `/calculator?${queryParams.toString()}`;
    }
}

// Event Listeners
searchInput.addEventListener('input', filterAndSortHistory);
sortSelect.addEventListener('change', filterAndSortHistory);
clearHistoryBtn.addEventListener('click', clearAllHistory);
confirmDeleteBtn.addEventListener('click', deleteHistoryItem);
cancelDeleteBtn.addEventListener('click', hideDeleteModal);

// Logout
logoutBtn.addEventListener('click', async () => {
    try {
        await auth.signOut();
        await fetch('/logout');
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout error:', error);
        showError('Error logging out. Please try again.');
    }
}); 