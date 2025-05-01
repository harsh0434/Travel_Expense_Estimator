document.addEventListener('DOMContentLoaded', function() {
    // Initialize Firebase
    const firebaseConfig = {
        apiKey: "AIzaSyAQIbXZd8Rj5PmX0O6WCvsAETgbc48E2Q8",
        authDomain: "travelmint-f010c.firebaseapp.com",
        projectId: "travelmint-f010c",
        storageBucket: "travelmint-f010c.firebasestorage.app",
        messagingSenderId: "758579092637",
        appId: "1:758579092637:web:673aeaac3121319a958874",
        measurementId: "G-WFPKGXJY6R"
    };

    // Initialize Firebase only once
    if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
        console.log('Firebase initialized');
    }

    const auth = firebase.auth();
    const db = firebase.firestore();

    // Set persistence to LOCAL before any auth operations
    auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL)
        .then(() => {
            console.log('Auth persistence set to LOCAL');
        })
        .catch((error) => {
            console.error('Persistence error:', error);
        });

    // Debug function to show auth state
    function debugAuthState(user) {
        console.log('Auth state changed:', user ? 'Logged in' : 'Logged out');
        if (user) {
            console.log('User email:', user.email);
            console.log('Email verified:', user.emailVerified);
            console.log('User ID:', user.uid);
        }
    }

    // Check Authentication State with debug logging
    auth.onAuthStateChanged((user) => {
        debugAuthState(user);
        const path = window.location.pathname;
        console.log('Current path:', path);

        if (path === '/login') {
            if (user) {
                console.log('User is logged in, redirecting to home');
                window.location.href = '/home';
            }
        } else if (["/home", "/calculator", "/profile"].includes(path)) {
            if (!user) {
                console.log('User is not logged in on protected page');
                const mainContent = document.getElementById('main-content');
                if (mainContent) {
                    mainContent.innerHTML = '<div style="color:#c62828; font-size:1.2rem; text-align:center; margin-top:2rem;">You must be logged in to view this page.</div>';
                }
            }
        }
    });

    // DOM Elements
    const loginTab = document.querySelector('.auth-tab[data-tab="login"]');
    const signupTab = document.querySelector('.auth-tab[data-tab="signup"]');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');

    // Password Toggle Elements
    const loginPassword = document.getElementById('loginPassword');
    const signupPassword = document.getElementById('signupPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');

    // Google Buttons
    const googleLoginBtn = document.getElementById('googleLogin');
    const googleSignupBtn = document.getElementById('googleSignup');

    // Phone Verification (Firebase Phone Auth)
    // Add a simple phone verification form logic
    const phoneForm = document.getElementById('phoneForm');
    const phoneInput = document.getElementById('phoneInput');
    const phoneCodeInput = document.getElementById('phoneCodeInput');
    const sendCodeBtn = document.getElementById('sendCodeBtn');
    const verifyCodeBtn = document.getElementById('verifyCodeBtn');
    let confirmationResult = null;

    // Tab Switching
    if (loginTab && signupTab && loginForm && signupForm) {
        loginTab.addEventListener('click', () => {
            loginTab.classList.add('active');
            signupTab.classList.remove('active');
            loginForm.classList.add('active');
            signupForm.classList.remove('active');
            clearMessages();
        });
        signupTab.addEventListener('click', () => {
            signupTab.classList.add('active');
            loginTab.classList.remove('active');
            signupForm.classList.add('active');
            loginForm.classList.remove('active');
            clearMessages();
        });
    }

    // Password Visibility Toggle
    togglePasswordButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            if (input) {
                input.type = input.type === 'password' ? 'text' : 'password';
            }
        });
    });

    // Message Display Functions
    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        }
        if (successMessage) successMessage.style.display = 'none';
    }
    function showSuccess(message) {
        if (successMessage) {
            successMessage.textContent = message;
            successMessage.style.display = 'block';
        }
        if (errorMessage) errorMessage.style.display = 'none';
    }
    function clearMessages() {
        if (errorMessage) errorMessage.style.display = 'none';
        if (successMessage) successMessage.style.display = 'none';
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
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearMessages();
            const email = document.getElementById('loginEmail').value;
            const password = loginPassword.value;
            
            try {
                console.log('Attempting login for:', email);
                const userCredential = await auth.signInWithEmailAndPassword(email, password);
                console.log('Login successful:', userCredential.user.email);
                
                if (!userCredential.user.emailVerified) {
                    showError('Please verify your email before logging in.');
                    await auth.signOut();
                    return;
                }
                
                showSuccess('Login successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/home';
                }, 1500);
            } catch (error) {
                console.error('Login error:', error);
                showError(error.message);
            }
        });
    }

    // Signup Form Submit
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearMessages();
            const email = document.getElementById('signupEmail').value;
            const password = signupPassword.value;
            const confirm = confirmPassword.value;
            if (!validateEmail(email)) {
                showError('Please enter a valid email address');
                return;
            }
            if (!validatePassword(password)) {
                showError('Password must be at least 6 characters long');
                return;
            }
            if (password !== confirm) {
                showError('Passwords do not match');
                return;
            }
            try {
                const userCredential = await auth.createUserWithEmailAndPassword(email, password);
                await userCredential.user.sendEmailVerification();
                showSuccess('Account created! Please verify your email before logging in.');
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
    }

    // Google Sign In (for both login and signup)
    function googleSignIn() {
        clearMessages();
        const provider = new firebase.auth.GoogleAuthProvider();
        auth.signInWithPopup(provider)
            .then(() => {
                showSuccess('Signed in with Google successfully! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/home';
                }, 1500);
            })
            .catch((error) => {
                if (error.code === 'auth/popup-blocked') {
                    showError('Please allow popups for this website');
                } else {
                    showError('An error occurred during Google sign-in');
                    console.error(error);
                }
            });
    }
    if (googleLoginBtn) googleLoginBtn.addEventListener('click', googleSignIn);
    if (googleSignupBtn) googleSignupBtn.addEventListener('click', googleSignIn);

    // Logout function
    async function logout() {
        try {
            await auth.signOut();
            window.location.href = '/login';
        } catch (error) {
            throw error;
        }
    }

    if (phoneForm && sendCodeBtn && verifyCodeBtn) {
        window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier('sendCodeBtn', {
            size: 'invisible',
            callback: function(response) {
                // reCAPTCHA solved
            }
        });

        sendCodeBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            clearMessages();
            const phoneNumber = phoneInput.value;
            if (!phoneNumber.match(/^\+\d{10,15}$/)) {
                showError('Enter a valid phone number with country code (e.g., +911234567890)');
                return;
            }
            try {
                confirmationResult = await auth.signInWithPhoneNumber(phoneNumber, window.recaptchaVerifier);
                showSuccess('Verification code sent! Check your SMS.');
            } catch (error) {
                showError('Error sending code: ' + error.message);
            }
        });

        verifyCodeBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            clearMessages();
            const code = phoneCodeInput.value;
            if (!code) {
                showError('Enter the verification code sent to your phone.');
                return;
            }
            try {
                await confirmationResult.confirm(code);
                showSuccess('Phone number verified!');
            } catch (error) {
                showError('Invalid code. Please try again.');
            }
        });
    }
}); 