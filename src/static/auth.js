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

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    const errorMessage = document.querySelector('.error-message');
    const successMessage = document.querySelector('.success-message');

    // Password Toggle Elements
    const toggleLoginPassword = document.getElementById('toggleLoginPassword');
    const toggleSignupPassword = document.getElementById('toggleSignupPassword');
    const loginPassword = document.getElementById('loginPassword');
    const signupPassword = document.getElementById('signupPassword');

    // Google Sign In Buttons
    const googleSignInButton = document.getElementById('googleSignIn');
    const googleSignInButton2 = document.getElementById('googleSignIn2');

    // Tab Switching
    function switchTab(activeTab, activeForm, inactiveTab, inactiveForm) {
        activeTab.classList.add('active');
        inactiveTab.classList.remove('active');
        activeForm.classList.add('active');
        inactiveForm.classList.remove('active');
        clearMessages();
        clearForms();
    }

    if (loginTab && signupTab && loginForm && signupForm) {
        loginTab.addEventListener('click', () => {
            switchTab(loginTab, loginForm, signupTab, signupForm);
        });

        signupTab.addEventListener('click', () => {
            switchTab(signupTab, signupForm, loginTab, loginForm);
        });
    }

    // Password Visibility Toggle
    function togglePasswordVisibility(passwordInput, toggleButton) {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        toggleButton.innerHTML = type === 'password' ? '👁️' : '👁️‍🗨️';
    }

    if (toggleLoginPassword && loginPassword) {
        toggleLoginPassword.addEventListener('click', () => {
            togglePasswordVisibility(loginPassword, toggleLoginPassword);
        });
    }

    if (toggleSignupPassword && signupPassword) {
        toggleSignupPassword.addEventListener('click', () => {
            togglePasswordVisibility(signupPassword, toggleSignupPassword);
        });
    }

    // Message Display Functions
    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            if (successMessage) successMessage.style.display = 'none';
        }
    }

    function showSuccess(message) {
        if (successMessage) {
            successMessage.textContent = message;
            successMessage.style.display = 'block';
            if (errorMessage) errorMessage.style.display = 'none';
        }
    }

    function clearMessages() {
        if (errorMessage) errorMessage.style.display = 'none';
        if (successMessage) successMessage.style.display = 'none';
    }

    function clearForms() {
        if (loginForm) loginForm.reset();
        if (signupForm) signupForm.reset();
    }

    // Form Validation
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function validatePassword(password) {
        return password.length >= 6;
    }

    // Login Form Handler
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = loginForm.querySelector('input[type="email"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;

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
                    window.location.href = '/';
                }, 1000);
            } catch (error) {
                console.error('Login error:', error);
                showError(error.message || 'Login failed. Please try again.');
            }
        });
    }

    // Email verification
    function sendEmailVerification(user) {
        user.sendEmailVerification().then(() => {
            alert('Verification email sent! Please check your inbox.');
        }).catch((error) => {
            console.error('Error sending verification email:', error);
            alert('Error sending verification email. Please try again.');
        });
    }

    // Phone verification
    function sendPhoneVerification(phoneNumber) {
        const appVerifier = window.recaptchaVerifier;
        auth.signInWithPhoneNumber(phoneNumber, appVerifier).then((confirmationResult) => {
            window.confirmationResult = confirmationResult;
            alert('Verification code sent!');
        }).catch((error) => {
            console.error('Error sending verification code:', error);
            alert('Error sending verification code. Please try again.');
        });
    }

    // Verify phone code
    function verifyPhoneCode(code) {
        window.confirmationResult.confirm(code).then((result) => {
            alert('Phone number verified successfully!');
        }).catch((error) => {
            console.error('Error verifying code:', error);
            alert('Invalid verification code. Please try again.');
        });
    }

    // Modify signup function to include verification
    function signup(email, password, name, phoneNumber) {
        auth.createUserWithEmailAndPassword(email, password)
            .then((userCredential) => {
                const user = userCredential.user;
                // Send email verification
                sendEmailVerification(user);
                
                // Send phone verification
                sendPhoneVerification(phoneNumber);
                
                // Save user data
                return db.collection('users').doc(user.uid).set({
                    name: name,
                    email: email,
                    phoneNumber: phoneNumber,
                    createdAt: firebase.firestore.FieldValue.serverTimestamp()
                });
            })
            .then(() => {
                alert('Account created successfully! Please verify your email and phone number.');
            })
            .catch((error) => {
                console.error('Error:', error);
                alert(error.message);
            });
    }

    // Signup Form Handler
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = signupForm.querySelector('input[type="email"]').value;
            const password = signupForm.querySelector('input[type="password"]').value;
            const name = signupForm.querySelector('input[type="name"]').value;
            const phoneNumber = signupForm.querySelector('input[type="phone"]').value;

            if (!validateEmail(email)) {
                showError('Please enter a valid email address');
                return;
            }

            if (!validatePassword(password)) {
                showError('Password must be at least 6 characters long');
                return;
            }

            try {
                signup(email, password, name, phoneNumber);
            } catch (error) {
                console.error('Signup error:', error);
                showError(error.message || 'Signup failed. Please try again.');
            }
        });
    }

    // Google Sign In Handler
    if (googleSignInButton) {
        googleSignInButton.addEventListener('click', async () => {
            try {
                const provider = new firebase.auth.GoogleAuthProvider();
                const result = await auth.signInWithPopup(provider);
                showSuccess('Google sign-in successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } catch (error) {
                console.error('Google sign in error:', error);
                showError(error.message || 'Google sign in failed. Please try again.');
            }
        });
    }

    if (googleSignInButton2) {
        googleSignInButton2.addEventListener('click', async () => {
            try {
                const provider = new firebase.auth.GoogleAuthProvider();
                const result = await auth.signInWithPopup(provider);
                showSuccess('Google sign-in successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } catch (error) {
                console.error('Google sign in error:', error);
                showError(error.message || 'Google sign in failed. Please try again.');
            }
        });
    }

    // Check Authentication State
    auth.onAuthStateChanged((user) => {
        if (user) {
            // User is signed in, only redirect if on login page
            if (window.location.pathname === '/login') {
                window.location.href = '/';
            }
        } else {
            // User is signed out, only redirect if not on login page
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
    });
});

// Logout function
async function logout() {
    try {
        await auth.signOut();
        window.location.href = '/login';
    } catch (error) {
        console.error('Logout error:', error);
        showError('Error logging out. Please try again.');
    }
} 