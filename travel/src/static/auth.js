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
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');
const userEmailDisplay = document.getElementById('user-email-display');
const logoutBtn = document.getElementById('logout-btn');

// Tab Switching
const authTabs = document.querySelectorAll('.auth-tab');
authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class from all tabs
        authTabs.forEach(t => t.classList.remove('active'));
        // Add active class to clicked tab
        tab.classList.add('active');
        
        // Hide all forms
        document.querySelectorAll('.auth-form').forEach(form => {
            form.classList.remove('active');
        });
        
        // Show selected form
        const formId = tab.dataset.tab === 'login' ? 'loginForm' : 'signupForm';
        document.getElementById(formId).classList.add('active');
        
        // Clear messages
        hideMessages();
    });
});

// Password Visibility Toggle
document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', () => {
        const input = button.previousElementSibling;
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        button.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
    });
});

// Message Display Functions
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
}

function hideMessages() {
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
}

// Input validation
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

// Login Form Handler
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();

    const email = loginForm.querySelector('#loginEmail').value;
    const password = loginForm.querySelector('#loginPassword').value;

    if (!validateEmail(email)) {
        showError('Please enter a valid email address');
        return;
    }

    if (!validatePassword(password)) {
        showError('Password must be at least 6 characters long');
        return;
    }

    try {
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        showSuccess('Login successful! Redirecting...');
        setTimeout(() => {
            window.location.href = '/home';
        }, 1500);
    } catch (error) {
        console.error('Login error:', error);
        showError(getErrorMessage(error.code));
    }
});

// Signup Form Handler
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();

    const email = signupForm.querySelector('#signupEmail').value;
    const password = signupForm.querySelector('#signupPassword').value;
    const confirmPassword = signupForm.querySelector('#confirmPassword').value;

    if (!validateEmail(email)) {
        showError('Please enter a valid email address');
        return;
    }

    if (!validatePassword(password)) {
        showError('Password must be at least 6 characters long');
        return;
    }

    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }

    try {
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        showSuccess('Account created successfully! Redirecting...');
        setTimeout(() => {
            window.location.href = '/home';
        }, 1500);
    } catch (error) {
        console.error('Signup error:', error);
        showError(getErrorMessage(error.code));
    }
});

// Google Sign In
document.querySelectorAll('#googleLogin, #googleSignup').forEach(button => {
    button.addEventListener('click', async () => {
        hideMessages();
        try {
            const provider = new firebase.auth.GoogleAuthProvider();
            const result = await auth.signInWithPopup(provider);
            showSuccess('Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = '/home';
            }, 1500);
        } catch (error) {
            console.error('Google sign in error:', error);
            showError(getErrorMessage(error.code));
        }
    });
});

// Logout Handler
if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
        try {
            await auth.signOut();
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout error:', error);
            alert('Error logging out. Please try again.');
        }
    });
}

// Error Message Helper
function getErrorMessage(errorCode) {
    switch (errorCode) {
        case 'auth/user-not-found':
            return 'No account found with this email address';
        case 'auth/wrong-password':
            return 'Incorrect password';
        case 'auth/email-already-in-use':
            return 'An account already exists with this email address';
        case 'auth/weak-password':
            return 'Password is too weak';
        case 'auth/invalid-email':
            return 'Invalid email address';
        case 'auth/operation-not-allowed':
            return 'Operation not allowed';
        case 'auth/popup-closed-by-user':
            return 'Google sign in was cancelled';
        default:
            return 'An error occurred. Please try again.';
    }
}

// Authentication State Observer
auth.onAuthStateChanged((user) => {
    if (user) {
        if (userEmailDisplay) {
            userEmailDisplay.textContent = user.email;
        }
        
        // Only redirect if we're on the login page
        if (window.location.pathname === '/login') {
            window.location.href = '/home';
        }
    } else {
        // If not logged in and not on login page, redirect to login
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }
}); 