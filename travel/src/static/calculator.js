// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAGh9t0LiLEVVp0Y5d5xc0QOxdNf2NP8rk",
    authDomain: "incredible-india-travel.firebaseapp.com",
    projectId: "incredible-india-travel",
    storageBucket: "incredible-india-travel.appspot.com",
    messagingSenderId: "655748510031",
    appId: "1:655748510031:web:3c45af99fa120290f41f0b"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// DOM Elements
const calculatorForm = document.getElementById('calculatorForm');
const resultsSection = document.getElementById('resultsSection');
const userEmail = document.getElementById('userEmail');
const logoutBtn = document.getElementById('logoutBtn');

// Cost display elements
const accommodationCost = document.getElementById('accommodationCost');
const foodCost = document.getElementById('foodCost');
const activitiesCost = document.getElementById('activitiesCost');
const transportCost = document.getElementById('transportCost');
const totalCost = document.getElementById('totalCost');
const tripSummary = document.getElementById('tripSummary');

// Authentication state observer
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        if (user.email) {
            userEmail.textContent = user.email;
        }
    } else {
        window.location.href = '/login';
    }
});

// Logout handler
logoutBtn.addEventListener('click', () => {
    firebase.auth().signOut()
        .then(() => {
            window.location.href = '/login';
        })
        .catch((error) => {
            console.error('Logout error:', error);
        });
});

// Helper function to format currency
function formatCurrency(amount) {
    return '₹' + amount.toLocaleString('en-IN');
}

// Form submission handler
calculatorForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const destination = document.getElementById('destination').value;
    const days = parseInt(document.getElementById('days').value);
    const people = parseInt(document.getElementById('people').value);
    const travelMode = document.getElementById('travelMode').value;
    const budgetLevel = document.getElementById('budgetLevel').value;

    // Log the form data for debugging
    console.log('Form data:', {
        destination,
        days,
        people,
        travelMode,
        budgetLevel
    });

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                destination,
                days,
                people,
                travel_mode: travelMode,
                budget_level: budgetLevel
            })
        });

        if (!response.ok) {
            throw new Error('Failed to calculate costs');
        }

        const data = await response.json();
        
        // Update the UI with the results
        accommodationCost.textContent = formatCurrency(data.predicted_costs.accommodation);
        foodCost.textContent = formatCurrency(data.predicted_costs.food);
        activitiesCost.textContent = formatCurrency(data.predicted_costs.activities);
        transportCost.textContent = formatCurrency(data.predicted_costs.transport);
        
        // Calculate and display total cost
        const total = data.total_cost;
        totalCost.textContent = formatCurrency(total);
        tripSummary.textContent = `${people} ${people > 1 ? 'people' : 'person'} for ${days} ${days > 1 ? 'days' : 'day'}`;

        // Show the results section with animation
        resultsSection.classList.add('show');
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        alert('Error calculating travel costs. Please try again.');
    }
}); 