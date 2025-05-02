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
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const auth = firebase.auth();
const db = firebase.firestore();

// Base costs for different budget levels
const budgetLevelMultipliers = {
    budget: 1,
    standard: 1.5,
    luxury: 2.5
};

// Base costs for different travel modes
const travelModeBaseCosts = {
    train: 800,
    bus: 600,
    flight: 3000,
    car: 1000
};

// Base costs for different destinations (per day)
const destinationBaseCosts = {
    // North India
    delhi: { accommodation: 2000, food: 800, activities: 1000 },
    agra: { accommodation: 1800, food: 700, activities: 1200 },
    jaipur: { accommodation: 1900, food: 750, activities: 1100 },
    varanasi: { accommodation: 1500, food: 600, activities: 800 },
    amritsar: { accommodation: 1600, food: 650, activities: 900 },
    shimla: { accommodation: 2200, food: 800, activities: 1000 },
    manali: { accommodation: 2000, food: 750, activities: 1200 },
    rishikesh: { accommodation: 1500, food: 600, activities: 1500 },
    ladakh: { accommodation: 2500, food: 900, activities: 2000 },
    srinagar: { accommodation: 2200, food: 800, activities: 1500 },
    mussoorie: { accommodation: 2300, food: 850, activities: 1100 },
    nainital: { accommodation: 2100, food: 800, activities: 1000 },
    haridwar: { accommodation: 1600, food: 600, activities: 900 },
    dharamshala: { accommodation: 1800, food: 700, activities: 1100 },
    dalhousie: { accommodation: 2000, food: 750, activities: 1200 },

    // South India
    bangalore: { accommodation: 2500, food: 900, activities: 1200 },
    mysore: { accommodation: 1800, food: 700, activities: 1000 },
    ooty: { accommodation: 2200, food: 800, activities: 1200 },
    chennai: { accommodation: 2300, food: 850, activities: 1100 },
    pondicherry: { accommodation: 2000, food: 750, activities: 1000 },
    hyderabad: { accommodation: 2200, food: 800, activities: 1100 },
    hampi: { accommodation: 1500, food: 600, activities: 800 },
    kerala: { accommodation: 2500, food: 900, activities: 1500 },
    goa: { accommodation: 3000, food: 1000, activities: 2000 },
    munnar: { accommodation: 2200, food: 800, activities: 1200 },
    kovalam: { accommodation: 2400, food: 850, activities: 1300 },
    varkala: { accommodation: 2000, food: 750, activities: 1100 },
    wayanad: { accommodation: 1900, food: 700, activities: 1200 },
    coorg: { accommodation: 2300, food: 850, activities: 1300 },
    mahabalipuram: { accommodation: 2100, food: 800, activities: 1100 },

    // West India
    mumbai: { accommodation: 3000, food: 1000, activities: 1500 },
    udaipur: { accommodation: 2200, food: 800, activities: 1200 },
    jaisalmer: { accommodation: 1800, food: 700, activities: 1300 },
    jodhpur: { accommodation: 1900, food: 750, activities: 1100 },
    mount_abu: { accommodation: 2000, food: 800, activities: 1000 },
    pune: { accommodation: 2500, food: 900, activities: 1100 },
    ahmedabad: { accommodation: 2000, food: 800, activities: 1000 },
    kutch: { accommodation: 1800, food: 700, activities: 1200 },
    nashik: { accommodation: 1900, food: 750, activities: 900 },
    lonavala: { accommodation: 2200, food: 850, activities: 1000 },

    // East India
    kolkata: { accommodation: 2200, food: 800, activities: 1100 },
    darjeeling: { accommodation: 2000, food: 750, activities: 1200 },
    gangtok: { accommodation: 2200, food: 800, activities: 1300 },
    puri: { accommodation: 1800, food: 700, activities: 1000 },
    sundarbans: { accommodation: 2000, food: 750, activities: 1500 },
    shillong: { accommodation: 2100, food: 800, activities: 1200 },
    kaziranga: { accommodation: 2300, food: 850, activities: 1400 },
    tawang: { accommodation: 2000, food: 750, activities: 1300 },
    cherrapunji: { accommodation: 1900, food: 700, activities: 1100 },
    majuli: { accommodation: 1700, food: 650, activities: 1000 }
};

document.addEventListener('DOMContentLoaded', () => {
    const calculatorForm = document.getElementById('calculatorForm');
    const resultsSection = document.getElementById('results');
    const logoutBtn = document.getElementById('logoutBtn');

    // Check authentication
    auth.onAuthStateChanged((user) => {
        if (!user) {
            window.location.href = '/login';
        } else {
            document.getElementById('userEmail').textContent = user.email;
        }
        });

    // Form submission handler
    if (calculatorForm) {
        calculatorForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Get form values
            const destination = document.getElementById('destination').value;
            const days = parseInt(document.getElementById('days').value);
            const people = parseInt(document.getElementById('people').value);
            const travelMode = document.getElementById('travel_mode').value;
            const budgetLevel = document.getElementById('budget_level').value;

            // Validate inputs
            if (!destination || isNaN(days) || isNaN(people) || !travelMode || !budgetLevel) {
                alert('Please fill in all fields correctly');
                return;
            }

            // Get base costs for the selected destination
            const baseCosts = destinationBaseCosts[destination];
            if (!baseCosts) {
                alert('Please select a valid destination');
                return;
            }

            const budgetMultiplier = budgetLevelMultipliers[budgetLevel];
            const travelCost = travelModeBaseCosts[travelMode];

            // Calculate costs
            const accommodationCost = baseCosts.accommodation * days * budgetMultiplier;
            const foodCost = baseCosts.food * days * people * budgetMultiplier;
            const transportCost = travelCost * people * 2; // Round trip
            const activitiesCost = baseCosts.activities * days * people * budgetMultiplier;

            const totalCost = accommodationCost + foodCost + transportCost + activitiesCost;

            // Format numbers
            const formatNumber = (num) => num.toLocaleString('en-IN');
                
            // Update UI
            document.getElementById('accommodation-cost').textContent = formatNumber(Math.round(accommodationCost));
            document.getElementById('food-cost').textContent = formatNumber(Math.round(foodCost));
            document.getElementById('transport-cost').textContent = formatNumber(Math.round(transportCost));
            document.getElementById('activities-cost').textContent = formatNumber(Math.round(activitiesCost));
            document.getElementById('total-cost').textContent = formatNumber(Math.round(totalCost));
            document.getElementById('total-people').textContent = people;
            document.getElementById('total-days').textContent = days;
                
            // Show results section
            resultsSection.style.display = 'block';
            setTimeout(() => {
                resultsSection.classList.add('show');
            }, 10);

            // Save to history
            try {
                const user = auth.currentUser;
                if (user) {
                    await db.collection('users').doc(user.uid).collection('history').add({
                        destination: destination,
                        days: days,
                        people: people,
                        travelMode: travelMode,
                        budgetLevel: budgetLevel,
                        totalCost: totalCost,
                        timestamp: firebase.firestore.FieldValue.serverTimestamp(),
                        breakdown: {
                            accommodation: accommodationCost,
                            food: foodCost,
                            transport: transportCost,
                            activities: activitiesCost
                        }
                    });
                }
            } catch (error) {
                console.error('Error saving to history:', error);
            }
        });
    }

    // Logout handler
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await auth.signOut();
                await fetch('/logout', { method: 'POST' });
                window.location.href = '/login';
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }
}); 