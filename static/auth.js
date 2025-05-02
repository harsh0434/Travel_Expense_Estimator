document.addEventListener('DOMContentLoaded', function() {
    // Initialize Firebase
    const firebaseConfig = {
        apiKey: "AIzaSyD-KNs5W-18FF60nVhncJD0lyD8BAC03w4",
        authDomain: "travel-expense-e160e.firebaseapp.com",
        projectId: "travel-expense-e160e",
        storageBucket: "travel-expense-e160e.firebasestorage.app",
        messagingSenderId: "193251517541",
        appId: "1:193251517541:web:90653d68d54c2c68c1128c"
    };

    if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
    }
    const auth = firebase.auth();
    const db = firebase.firestore();

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
                const user = userCredential.user;
                // Update server session
                await fetch('/auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: user.uid })
                });
                showSuccess('Login successful!');
                window.location.href = '/home';
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
                const user = userCredential.user;
                // Update server session
                await fetch('/auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: user.uid })
                });
                showSuccess('Account created successfully!');
                window.location.href = '/home';
            } catch (error) {
                console.error('Signup error:', error);
                showError(error.message);
            }
        });
    }

    // Google Sign In (for both login and signup)
    function googleSignIn() {
        clearMessages();
        const provider = new firebase.auth.GoogleAuthProvider();
        auth.signInWithPopup(provider)
            .then(async (result) => {
                const user = result.user;
                // Update server session
                await fetch('/auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: user.uid })
                });
                showSuccess('Login successful!');
                window.location.href = '/home';
            })
            .catch((error) => {
                console.error('Google sign-in error:', error);
                showError(error.message);
            });
    }
    if (googleLoginBtn) googleLoginBtn.addEventListener('click', googleSignIn);
    if (googleSignupBtn) googleSignupBtn.addEventListener('click', googleSignIn);

    // Check Authentication State
    firebase.auth().onAuthStateChanged(async (user) => {
        if (user) {
            // User is signed in
            try {
                // Update server session
                await fetch('/auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: user.uid })
                });
                
                // Only redirect if we're on the login page
                if (window.location.pathname === '/login') {
                    window.location.href = '/home';
                }
            } catch (error) {
                console.error('Error updating session:', error);
            }
        } else {
            // User is signed out
            // Only redirect to login if we're not already on the login page
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
    });

    // Logout function
    async function logout() {
        try {
            await auth.signOut();
            await fetch('/logout', { method: 'POST' });
            showSuccess('Logged out successfully!');
        } catch (error) {
            console.error('Error during logout:', error);
            showError('Error during logout');
        }
    }

    // Set Firebase Auth persistence to LOCAL
    firebase.auth().setPersistence(firebase.auth.Auth.Persistence.LOCAL)
      .catch(function(error) {
        console.error('Persistence error:', error);
      });
}); 