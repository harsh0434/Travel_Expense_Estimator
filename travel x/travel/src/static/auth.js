// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyDQKOtxwJ8YPgmPGGhJc3Ry_XxDZQq2aDU",
    authDomain: "incredible-india-travel.firebaseapp.com",
    projectId: "incredible-india-travel",
    storageBucket: "incredible-india-travel.appspot.com",
    messagingSenderId: "1098977653977",
    appId: "1:1098977653977:web:b2c9f6f1d8bcf4b4b7c5b4"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// DOM Elements
const loginTab = document.getElementById('loginTab');
const signupTab = document.getElementById('signupTab');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const errorMessage = document.querySelector('.error-message');
const successMessage = document.querySelector('.success-message');

// Password Toggle Elements
const toggleLoginPassword = document.getElementById('toggleLoginPassword');
const toggleSignupPassword = document.getElementById('toggleSignupPassword');
const loginPassword = document.getElementById('loginPassword');
const signupPassword = document.getElementById('signupPassword');

// Tab Switching
function switchTab(activeTab, activeForm, inactiveTab, inactiveForm) {
    activeTab.classList.add('active');
    inactiveTab.classList.remove('active');
    activeForm.classList.add('active');
    inactiveForm.classList.remove('active');
    clearMessages();
    clearForms();
}

loginTab.addEventListener('click', () => {
    switchTab(loginTab, loginForm, signupTab, signupForm);
});

signupTab.addEventListener('click', () => {
    switchTab(signupTab, signupForm, loginTab, loginForm);
});

// Password Visibility Toggle
function togglePasswordVisibility(passwordInput, toggleButton) {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
    toggleButton.innerHTML = type === 'password' ? '👁️' : '👁️‍🗨️';
}

toggleLoginPassword.addEventListener('click', () => {
    togglePasswordVisibility(loginPassword, toggleLoginPassword);
});

toggleSignupPassword.addEventListener('click', () => {
    togglePasswordVisibility(signupPassword, toggleSignupPassword);
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

function clearMessages() {
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
}

function clearForms() {
    loginForm.reset();
    signupForm.reset();
}

// Form Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

// Login Form Submit
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();

    const email = document.getElementById('loginEmail').value;
    const password = loginPassword.value;

    if (!validateEmail(email)) {
        showError('Please enter a valid email address');
        return;
    }

    if (!validatePassword(password)) {
        showError('Password must be at least 6 characters long');
        return;
    }

    try {
        await auth.signInWithEmailAndPassword(email, password);
        showSuccess('Login successful! Redirecting...');
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
    } catch (error) {
        switch (error.code) {
            case 'auth/user-not-found':
                showError('No account found with this email');
                break;
            case 'auth/wrong-password':
                showError('Incorrect password');
                break;
            default:
                showError('An error occurred during login');
                console.error(error);
        }
    }
});

// Signup Form Submit
signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();

    const email = document.getElementById('signupEmail').value;
    const password = signupPassword.value;
    const name = document.getElementById('signupName').value;

    if (!name.trim()) {
        showError('Please enter your name');
        return;
    }

    if (!validateEmail(email)) {
        showError('Please enter a valid email address');
        return;
    }

    if (!validatePassword(password)) {
        showError('Password must be at least 6 characters long');
        return;
    }

    try {
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        await db.collection('users').doc(userCredential.user.uid).set({
            name: name,
            email: email,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        await userCredential.user.updateProfile({
            displayName: name
        });

        showSuccess('Account created successfully! Redirecting...');
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
    } catch (error) {
        switch (error.code) {
            case 'auth/email-already-in-use':
                showError('An account with this email already exists');
                break;
            case 'auth/invalid-email':
                showError('Invalid email address');
                break;
            case 'auth/weak-password':
                showError('Password is too weak');
                break;
            default:
                showError('An error occurred during signup');
                console.error(error);
        }
    }
});

// Google Sign In
const googleSignInButton = document.getElementById('googleSignIn');

googleSignInButton.addEventListener('click', async () => {
    clearMessages();
    const provider = new firebase.auth.GoogleAuthProvider();
    
    try {
        const result = await auth.signInWithPopup(provider);
        const user = result.user;
        
        // Check if user document exists
        const userDoc = await db.collection('users').doc(user.uid).get();
        
        if (!userDoc.exists) {
            // Create user document if it doesn't exist
            await db.collection('users').doc(user.uid).set({
                name: user.displayName,
                email: user.email,
                createdAt: firebase.firestore.FieldValue.serverTimestamp()
            });
        }
        
        showSuccess('Signed in with Google successfully! Redirecting...');
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
    } catch (error) {
        if (error.code === 'auth/popup-blocked') {
            showError('Please allow popups for this website');
        } else {
            showError('An error occurred during Google sign-in');
            console.error(error);
        }
    }
});

// Check Authentication State
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        if (window.location.pathname === '/login') {
            window.location.href = '/home';
        }
    } else {
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }
});

// Logout function
async function logout() {
    try {
        await auth.signOut();
        window.location.href = '/login';
    } catch (error) {
        throw error;
    }
} 