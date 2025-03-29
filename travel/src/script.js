// Indian destinations with their regions
const indianDestinations = {
    // North India
    'delhi': 'north india',
    'agra': 'north india',
    'jaipur': 'north india',
    'varanasi': 'north india',
    'amritsar': 'north india',
    'shimla': 'north india',
    'manali': 'north india',
    'ladakh': 'north india',
    'rishikesh': 'north india',
    'haridwar': 'north india',
    
    // South India
    'bangalore': 'south india',
    'mysore': 'south india',
    'ooty': 'south india',
    'chennai': 'south india',
    'pondicherry': 'south india',
    'hyderabad': 'south india',
    'hampi': 'south india',
    'kerala backwaters': 'south india',
    'munnar': 'south india',
    'kovalam': 'south india',
    
    // East India
    'kolkata': 'east india',
    'darjeeling': 'east india',
    'gangtok': 'east india',
    'puri': 'east india',
    'sundarbans': 'east india',
    'shillong': 'east india',
    'kaziranga': 'east india',
    'tawang': 'east india',
    'bodhgaya': 'east india',
    'majuli': 'east india',
    
    // West India
    'mumbai': 'west india',
    'goa': 'west india',
    'udaipur': 'west india',
    'jodhpur': 'west india',
    'jaisalmer': 'west india',
    'mount abu': 'west india',
    'kutch': 'west india',
    'ajanta & ellora caves': 'west india',
    'dwarka': 'west india',
    'diu': 'west india',
    
    // Central India
    'khajuraho': 'central india',
    'orchha': 'central india',
    'sanchi': 'central india',
    'bhopal': 'central india',
    'pachmarhi': 'central india',
    'kanha': 'central india',
    'bandhavgarh': 'central india',
    'gwalior': 'central india',
    'mandu': 'central india',
    'bhimbetka': 'central india'
};

// Base costs per person per day for different budget levels (in INR)
const baseCosts = {
    'low': {
        'accommodation': 1000,    // Basic hotel/hostel
        'food': 500,              // Basic meals
        'activities': 300,        // Basic sightseeing
        'transport': 500          // Local transport
    },
    'mid': {
        'accommodation': 2500,    // Mid-range hotel
        'food': 1000,             // Mid-range restaurants
        'activities': 800,        // Guided tours
        'transport': 1000         // Comfortable transport
    },
    'high': {
        'accommodation': 5000,    // Luxury hotel
        'food': 2000,             // Fine dining
        'activities': 1500,       // Premium activities
        'transport': 2000         // Private transport
    }
};

// Region multipliers for Indian regions
const regionMultipliers = {
    'north india': 1.1,  // Higher due to tourist popularity and extreme weather conditions
    'south india': 0.9,  // Moderate costs
    'east india': 0.8,   // Generally lower costs
    'west india': 1.2,   // Higher due to tourist destinations and business centers
    'central india': 0.7 // Lower costs due to less tourist traffic
};

// Travel mode multipliers
const modeMultipliers = {
    'car': 0.8,
    'bus': 0.6,
    'train': 1.0,
    'airways': 1.5
};

// Populate destination dropdown
function populateDestinations() {
    const destinationSelect = document.getElementById('destination');
    const destinations = Object.keys(indianDestinations).sort();
    
    destinations.forEach(dest => {
        const option = document.createElement('option');
        option.value = dest;
        option.textContent = dest.charAt(0).toUpperCase() + dest.slice(1);
        destinationSelect.appendChild(option);
    });
}

// Format number with Indian Rupee symbol and thousands separator
function formatCurrency(amount) {
    return '₹' + amount.toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

// Calculate travel cost
async function calculateTravelCost(days, people, travelMode, budget, region) {
    try {
        // Make API call to the Flask prediction endpoint
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                destination: region.split(' ')[0], // Use first word of region as destination
                region: region,
                days: parseInt(days),
                people: parseInt(people),
                travel_mode: travelMode.toLowerCase(),
                budget_level: budget.toLowerCase()
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to get prediction');
        }

        const prediction = await response.json();
        
        return {
            totalCost: prediction.total_cost,
            dailyCosts: prediction.predicted_costs
        };
    } catch (error) {
        console.error('Prediction error:', error);
        // Fallback to the basic calculation if prediction fails
        return calculateBasicTravelCost(days, people, travelMode, budget, region);
    }
}

// Fallback calculation function
function calculateBasicTravelCost(days, people, travelMode, budget, region) {
    // Get base costs for selected budget
    const dailyCosts = { ...baseCosts[budget.toLowerCase()] };
    if (!dailyCosts) {
        throw new Error('Invalid budget level');
    }
    
    // Apply region multiplier
    const regionMult = regionMultipliers[region.toLowerCase()] || 1;
    
    // Calculate daily costs per person with multipliers
    const adjustedCosts = {
        accommodation: Math.round(dailyCosts.accommodation * regionMult),
        food: Math.round(dailyCosts.food * regionMult),
        activities: Math.round(dailyCosts.activities * regionMult),
        transport: Math.round(dailyCosts.transport * modeMultipliers[travelMode.toLowerCase()])
    };
    
    // Calculate total daily cost per person
    const totalDailyPerPerson = Object.values(adjustedCosts).reduce((a, b) => a + b, 0);
    
    // Calculate total cost for all people and all days
    const totalCost = totalDailyPerPerson * days * people;
    
    return {
        totalCost,
        dailyCosts: adjustedCosts
    };
}

// Update results in the UI
function updateResults(result, days, people, travelMode) {
    const resultSection = document.getElementById('result');
    resultSection.style.display = 'block';
    
    // Update total cost
    document.getElementById('totalCost').textContent = formatCurrency(result.totalCost);
    
    // Update per-person and per-day costs
    document.getElementById('perPersonCost').textContent = formatCurrency(result.perPersonCost);
    document.getElementById('perDayCost').textContent = formatCurrency(result.perDayCost);
    
    // Update daily breakdown
    document.getElementById('accommodationCost').textContent = formatCurrency(result.dailyCosts.accommodation);
    document.getElementById('foodCost').textContent = formatCurrency(result.dailyCosts.food);
    document.getElementById('activitiesCost').textContent = formatCurrency(result.dailyCosts.activities);
    document.getElementById('transportCost').textContent = formatCurrency(result.dailyCosts.transport);
    
    // Update transportation details
    const transportDetails = document.getElementById('transportDetails');
    switch(travelMode) {
        case 'car':
            transportDetails.textContent = 'Estimated fuel cost included in transportation';
            break;
        case 'bus':
            transportDetails.textContent = 'Bus tickets included in transportation';
            break;
        case 'train':
            transportDetails.textContent = 'Train tickets included in transportation';
            break;
        case 'airways':
            transportDetails.textContent = 'Air tickets included in transportation';
            break;
    }
}

// Main calculation function
function calculateCost() {
    // Get form values
    const destination = document.getElementById('destination').value;
    const days = parseInt(document.getElementById('days').value);
    const people = parseInt(document.getElementById('people').value);
    const travelMode = document.getElementById('travelMode').value;
    const budget = document.getElementById('budget').value;
    
    // Validate inputs
    if (!destination || !days || !people || !travelMode || !budget) {
        alert('Please fill in all fields');
        return;
    }
    
    if (days < 1 || days > 30) {
        alert('Number of days must be between 1 and 30');
        return;
    }
    
    if (people < 1 || people > 10) {
        alert('Number of people must be between 1 and 10');
        return;
    }
    
    // Get region for the selected destination
    const region = indianDestinations[destination];
    
    // Calculate costs
    const result = calculateTravelCost(days, people, travelMode, budget, region);
    
    // Update results in the UI
    updateResults(result, days, people, travelMode);
}

// Initialize the page
document.addEventListener('DOMContentLoaded', populateDestinations);

// Firebase configuration
const firebaseConfig = {
    // Replace with your Firebase config
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
const authSection = document.getElementById('auth-section');
const calculatorSection = document.getElementById('calculator-section');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const verificationForm = document.getElementById('verification-form');
const userInfo = document.getElementById('user-info');
const logoutBtn = document.getElementById('logout-btn');
const calculatorForm = document.getElementById('calculator-form');
const resultSection = document.getElementById('result-section');

// Authentication State Observer
auth.onAuthStateChanged((user) => {
    if (user) {
        if (user.emailVerified) {
            showCalculator();
            updateUserInfo(user);
        } else {
            showVerification();
        }
    } else {
        showLogin();
    }
});

// Logging function
async function logInteraction(action, data) {
    try {
        const user = auth.currentUser;
        if (!user) {
            console.warn('User not authenticated, skipping log');
            return;
        }

        // Create a logs collection reference
        const logRef = db.collection('logs');
        
        const logData = {
            userId: user.uid,
            timestamp: firebase.firestore.FieldValue.serverTimestamp(),
            action,
            data: JSON.parse(JSON.stringify(data)), // Sanitize data
            userEmail: user.email
        };

        await logRef.add(logData);
        console.log('Interaction logged successfully');
    } catch (error) {
        // Log error but don't throw to prevent disrupting user experience
        console.error('Error logging interaction:', error);
    }
}

// Login Function
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = loginForm.email.value;
    const password = loginForm.password.value;

    try {
        await auth.signInWithEmailAndPassword(email, password);
        await logInteraction('login', { email, success: true });
        showCalculator();
    } catch (error) {
        await logInteraction('login', { email, success: false, error: error.message });
        alert(error.message);
    }
});

// Input validation functions
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/;
    return passwordRegex.test(password);
}

function validatePhone(phone) {
    // Indian phone number format
    const phoneRegex = /^[6-9]\d{9}$/;
    return phoneRegex.test(phone);
}

function validateCalculatorInputs(formData) {
    const errors = [];

    if (!formData.destination) {
        errors.push('Please select a destination');
    }

    if (!formData.days || formData.days < 1 || formData.days > 30) {
        errors.push('Number of days must be between 1 and 30');
    }

    if (!formData.people || formData.people < 1 || formData.people > 10) {
        errors.push('Number of people must be between 1 and 10');
    }

    if (!formData.travelMode) {
        errors.push('Please select a travel mode');
    }

    if (!formData.budget) {
        errors.push('Please select a budget level');
    }

    return errors;
}

// Error handling function
function handleError(error, context) {
    console.error(`Error in ${context}:`, error);
    logInteraction('error', { context, error: error.message });
    
    let userMessage = 'An error occurred. Please try again.';
    
    switch (error.code) {
        case 'auth/email-already-in-use':
            userMessage = 'This email is already registered. Please use a different email.';
            break;
        case 'auth/invalid-email':
            userMessage = 'Please enter a valid email address.';
            break;
        case 'auth/weak-password':
            userMessage = 'Password should be at least 8 characters long with 1 uppercase, 1 lowercase, and 1 number.';
            break;
        case 'auth/user-not-found':
            userMessage = 'No account found with this email. Please sign up first.';
            break;
        case 'auth/wrong-password':
            userMessage = 'Incorrect password. Please try again.';
            break;
        case 'permission-denied':
            userMessage = 'You do not have permission to perform this action.';
            break;
    }
    
    alert(userMessage);
}

// Signup Function
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = signupForm.email.value;
    const password = signupForm.password.value;
    const phone = signupForm.phone.value;

    // Validate inputs
    if (!validateEmail(email)) {
        alert('Please enter a valid email address');
        return;
    }

    if (!validatePassword(password)) {
        alert('Password must be at least 8 characters long with 1 uppercase, 1 lowercase, and 1 number');
        return;
    }

    if (!validatePhone(phone)) {
        alert('Please enter a valid Indian phone number');
        return;
    }

    try {
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        await userCredential.user.updateProfile({
            phoneNumber: phone
        });
        await userCredential.user.sendEmailVerification();
        await logInteraction('signup', { email, phone, success: true });
        showVerification();
    } catch (error) {
        handleError(error, 'signup');
    }
});

// Resend Verification Email
document.getElementById('resend-verification').addEventListener('click', async () => {
    try {
        await auth.currentUser.sendEmailVerification();
        alert('Verification email sent!');
    } catch (error) {
        alert(error.message);
    }
});

// Logout Function
logoutBtn.addEventListener('click', async () => {
    try {
        await auth.signOut();
        showLogin();
    } catch (error) {
        alert(error.message);
    }
});

// Form Navigation
document.querySelectorAll('.auth-form a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = e.target.getAttribute('href').substring(1);
        showForm(target);
    });
});

// Show/Hide Functions
function showLogin() {
    authSection.style.display = 'flex';
    calculatorSection.style.display = 'none';
    showForm('login');
}

function showSignup() {
    showForm('signup');
}

function showVerification() {
    showForm('verification');
}

function showCalculator() {
    authSection.style.display = 'none';
    calculatorSection.style.display = 'block';
}

function showForm(formId) {
    document.querySelectorAll('.auth-form').forEach(form => {
        form.style.display = 'none';
    });
    document.getElementById(formId + '-form').style.display = 'flex';
}

// Backup and Recovery Functions
async function backupUserData() {
    if (!auth.currentUser) return;

    try {
        // Get user's calculations
        const calculationsSnapshot = await db.collection('calculations')
            .where('userId', '==', auth.currentUser.uid)
            .get();

        const calculations = [];
        calculationsSnapshot.forEach(doc => {
            calculations.push({
                id: doc.id,
                ...doc.data()
            });
        });

        // Create backup data
        const backupData = {
            userId: auth.currentUser.uid,
            email: auth.currentUser.email,
            phoneNumber: auth.currentUser.phoneNumber,
            calculations,
            timestamp: new Date().toISOString()
        };

        // Save backup to Firestore
        await db.collection('backups').add(backupData);
        await logInteraction('backup', { success: true });
        alert('Backup created successfully!');
    } catch (error) {
        handleError(error, 'backup');
    }
}

async function restoreUserData(backupId) {
    if (!auth.currentUser) return;

    try {
        // Get backup data
        const backupDoc = await db.collection('backups').doc(backupId).get();
        if (!backupDoc.exists) {
            throw new Error('Backup not found');
        }

        const backupData = backupDoc.data();

        // Verify backup belongs to current user
        if (backupData.userId !== auth.currentUser.uid) {
            throw new Error('Unauthorized access to backup');
        }

        // Delete existing calculations
        const existingCalculations = await db.collection('calculations')
            .where('userId', '==', auth.currentUser.uid)
            .get();

        const batch = db.batch();
        existingCalculations.forEach(doc => {
            batch.delete(doc.ref);
        });

        // Restore calculations from backup
        backupData.calculations.forEach(calc => {
            const newRef = db.collection('calculations').doc();
            batch.set(newRef, {
                ...calc,
                id: newRef.id,
                userId: auth.currentUser.uid,
                restoredAt: firebase.firestore.FieldValue.serverTimestamp()
            });
        });

        // Commit the batch
        await batch.commit();
        await logInteraction('restore', { backupId, success: true });
        alert('Data restored successfully!');
    } catch (error) {
        handleError(error, 'restore');
    }
}

// Add backup/restore buttons to the UI
function addBackupRestoreUI() {
    const userInfo = document.getElementById('user-info');
    
    const backupButton = document.createElement('button');
    backupButton.textContent = 'Backup Data';
    backupButton.className = 'backup-btn';
    backupButton.onclick = backupUserData;
    
    const restoreButton = document.createElement('button');
    restoreButton.textContent = 'Restore Data';
    restoreButton.className = 'restore-btn';
    restoreButton.onclick = () => {
        const backupId = prompt('Enter backup ID to restore:');
        if (backupId) {
            restoreUserData(backupId);
        }
    };
    
    userInfo.appendChild(backupButton);
    userInfo.appendChild(restoreButton);
}

// Update the updateUserInfo function to include backup/restore buttons
function updateUserInfo(user) {
    userInfo.style.display = 'flex';
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('user-phone').textContent = user.phoneNumber || 'Not verified';
    addBackupRestoreUI();
}

// Calculator Functions
function displayResults(result, formData) {
    if (!result || !formData) {
        console.error('Missing result or form data');
        return;
    }

    try {
        // Show the result section
        const resultSection = document.getElementById('result-section');
        if (resultSection) {
            resultSection.style.display = 'block';
        }
        
        // Calculate costs
        const totalCost = Math.round(result.totalCost);
        const numPeople = parseInt(formData.people);
        const perPersonCost = Math.round(totalCost / numPeople);
        
        // Update total cost display
        const totalCostElement = document.getElementById('total-cost');
        if (totalCostElement) {
            totalCostElement.textContent = totalCost.toLocaleString('en-IN');
        }
        
        // Update number of people
        const totalPeopleElement = document.getElementById('total-people');
        if (totalPeopleElement) {
            totalPeopleElement.textContent = numPeople;
        }
        
        // Update per person cost
        const perPersonElement = document.getElementById('per-person-cost');
        if (perPersonElement) {
            perPersonElement.textContent = perPersonCost.toLocaleString('en-IN');
        }
        
        // Update daily breakdown (these are already per person costs)
        const dailyCosts = {
            'daily-accommodation': result.dailyCosts.accommodation,
            'daily-food': result.dailyCosts.food,
            'daily-activities': result.dailyCosts.activities,
            'daily-transport': result.dailyCosts.transport
        };

        // Update each daily cost
        Object.entries(dailyCosts).forEach(([elementId, cost]) => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = Math.round(cost).toLocaleString('en-IN');
            }
        });

    } catch (error) {
        console.error('Error updating display:', error);
        alert('Error displaying results. Please try again.');
    }
}

// Form submission handler
document.getElementById('calculator-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    try {
        // Get form values
        const formData = {
            destination: document.getElementById('destination').value.toLowerCase(),
            days: parseInt(document.getElementById('days').value),
            people: parseInt(document.getElementById('people').value),
            travel_mode: document.getElementById('travelMode').value.toLowerCase(),
            budget_level: document.getElementById('budget').value.toLowerCase(),
            region: 'west india' // For Goa
        };

        console.log('Sending data:', formData); // Debug log

        // Make API call
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to get prediction');
        }

        const result = await response.json();
        console.log('Received result:', result); // Debug log

        // Update the display
        const resultSection = document.getElementById('result-section');
        resultSection.style.display = 'block';

        // Update total cost
        document.getElementById('total-cost').textContent = 
            Math.round(result.total_cost).toLocaleString('en-IN');

        // Update number of people
        document.getElementById('total-people').textContent = formData.people;

        // Calculate and update per person cost
        const perPersonCost = result.total_cost / formData.people;
        document.getElementById('per-person-cost').textContent = 
            Math.round(perPersonCost).toLocaleString('en-IN');

        // Update daily costs
        document.getElementById('daily-accommodation').textContent = 
            Math.round(result.predicted_costs.accommodation_cost).toLocaleString('en-IN');
        document.getElementById('daily-food').textContent = 
            Math.round(result.predicted_costs.food_cost).toLocaleString('en-IN');
        document.getElementById('daily-activities').textContent = 
            Math.round(result.predicted_costs.activities_cost).toLocaleString('en-IN');
        document.getElementById('daily-transport').textContent = 
            Math.round(result.predicted_costs.transport_cost).toLocaleString('en-IN');

    } catch (error) {
        console.error('Error:', error);
        alert('Error calculating travel cost: ' + error.message);
    }
}); 