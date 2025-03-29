// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyDxwXqXqXqXqXqXqXqXqXqXqXqXqXqXqXqX",
    authDomain: "incredible-india-travel.firebaseapp.com",
    projectId: "incredible-india-travel",
    storageBucket: "incredible-india-travel.appspot.com",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdef1234567890"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// DOM Elements
const profileLink = document.getElementById('profileLink');
const logoutBtn = document.getElementById('logoutBtn');
const searchInput = document.getElementById('searchInput');
const regionFilter = document.getElementById('regionFilter');
const destinationCards = document.querySelectorAll('.destination-card');

// Check authentication state
auth.onAuthStateChanged((user) => {
    if (user) {
        // User is signed in
        profileLink.style.display = 'block';
        logoutBtn.style.display = 'block';
    } else {
        // User is signed out
        window.location.href = '/login';
    }
});

// Logout handler
logoutBtn.addEventListener('click', () => {
    auth.signOut()
        .then(() => {
            window.location.href = '/login';
        })
        .catch((error) => {
            console.error('Error signing out:', error);
            alert('Error signing out. Please try again.');
        });
});

// Search and filter functionality
function filterDestinations() {
    const searchTerm = searchInput.value.toLowerCase();
    const selectedRegion = regionFilter.value;

    destinationCards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const location = card.querySelector('p').textContent.toLowerCase();
        const region = card.dataset.region;

        const matchesSearch = title.includes(searchTerm) || location.includes(searchTerm);
        const matchesRegion = !selectedRegion || region === selectedRegion;

        if (matchesSearch && matchesRegion) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Add event listeners
searchInput.addEventListener('input', filterDestinations);
regionFilter.addEventListener('change', filterDestinations);

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Animation on scroll
function animateOnScroll() {
    const elements = document.querySelectorAll('.destination-card');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}

// Add scroll event listener
window.addEventListener('scroll', animateOnScroll);
// Initial animation check
animateOnScroll(); 