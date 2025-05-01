// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const profileForm = document.getElementById('profileForm');
    const profilePicture = document.getElementById('profilePicture');
    const profilePictureInput = document.getElementById('profilePictureInput');
    const logoutBtn = document.getElementById('logoutBtn');
    const saveBtn = document.getElementById('saveBtn');
    const message = document.getElementById('message');
    const mobileInput = document.getElementById('mobile');

    // Show message function
    function showMessage(text, type = 'success') {
        message.textContent = text;
        message.className = `message ${type}`;
        message.style.display = 'block';
        setTimeout(() => {
            message.style.display = 'none';
        }, 3000);
    }

    // Format date for input field (YYYY-MM-DD)
    function formatDateForInput(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toISOString().split('T')[0];
    }

    // Validate mobile number
    function validateMobile(mobile) {
        const mobileRegex = /^[0-9]{10}$/;
        return mobileRegex.test(mobile);
    }

    // Validate date of birth (must be at least 18 years old)
    function validateDOB(dob) {
        const today = new Date();
        const birthDate = new Date(dob);
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        
        return age >= 18;
    }

    // Mobile number input formatting
    if (mobileInput) {
        mobileInput.addEventListener('input', (e) => {
            // Remove any non-digit characters
            let value = e.target.value.replace(/\D/g, '');
            // Limit to 10 digits
            value = value.substring(0, 10);
            e.target.value = value;
        });
    }

    // Load user profile data
    async function loadUserProfile(user) {
        if (!user) {
            window.location.href = '/login';
            return;
        }

        try {
            // Get user data from Firestore
            const userRef = firebase.firestore().collection('users').doc(user.uid);
            const doc = await userRef.get();

            // Set email field regardless of document existence
            document.getElementById('email').value = user.email || '';

            if (doc.exists) {
                const data = doc.data();
                // Update form fields
                document.getElementById('firstName').value = data.firstName || '';
                document.getElementById('lastName').value = data.lastName || '';
                document.getElementById('nickname').value = data.nickname || '';
                document.getElementById('mobile').value = data.mobile || '';
                document.getElementById('dob').value = formatDateForInput(data.dob) || '';
                
                // Load profile picture if exists
                if (data.profilePictureUrl) {
                    profilePicture.src = data.profilePictureUrl;
                }
            } else {
                // Create new user document if it doesn't exist
                await userRef.set({
                    email: user.email,
                    createdAt: firebase.firestore.FieldValue.serverTimestamp()
                });
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            if (error.code === 'permission-denied') {
                showMessage('You do not have permission to access this profile', 'error');
            } else {
                showMessage('Error loading profile data', 'error');
            }
        }
    }

    // Handle profile picture upload
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Validate file type
            if (!file.type.startsWith('image/')) {
                showMessage('Please select an image file', 'error');
                return;
            }

            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                showMessage('Image size should be less than 5MB', 'error');
                return;
            }

            try {
                saveBtn.disabled = true;
                const user = firebase.auth().currentUser;
                if (!user) throw new Error('No user logged in');

                // Create a loading message
                showMessage('Uploading profile picture...', 'success');

                // Upload image to Firebase Storage
                const storageRef = firebase.storage().ref(`profile_pictures/${user.uid}/${file.name}`);
                const snapshot = await storageRef.put(file);
                const downloadUrl = await snapshot.ref.getDownloadURL();

                // Update user profile picture URL in Firestore
                const userRef = firebase.firestore().collection('users').doc(user.uid);
                await userRef.update({
                    profilePictureUrl: downloadUrl,
                    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
                });

                // Update profile picture display
                profilePicture.src = downloadUrl;
                showMessage('Profile picture updated successfully');

            } catch (error) {
                console.error('Error uploading profile picture:', error);
                if (error.code === 'permission-denied') {
                    showMessage('You do not have permission to upload a profile picture', 'error');
                } else {
                    showMessage('Error uploading profile picture', 'error');
                }
            } finally {
                saveBtn.disabled = false;
            }
        });
    }

    // Handle profile form submission
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const user = firebase.auth().currentUser;
            if (!user) {
                showMessage('No user logged in', 'error');
                return;
            }

            try {
                saveBtn.disabled = true;
                saveBtn.textContent = 'Saving...';

                const firstName = document.getElementById('firstName').value.trim();
                const lastName = document.getElementById('lastName').value.trim();
                const nickname = document.getElementById('nickname').value.trim();
                const dob = document.getElementById('dob').value;
                const mobile = document.getElementById('mobile').value.trim();

                // Validate required fields
                if (!firstName || !lastName || !nickname || !dob || !mobile) {
                    throw new Error('All required fields must be filled');
                }

                // Validate mobile number
                if (!validateMobile(mobile)) {
                    throw new Error('Please enter a valid 10-digit mobile number');
                }

                // Validate date of birth
                if (!validateDOB(dob)) {
                    throw new Error('You must be at least 18 years old to create a profile');
                }

                // Update user profile in Firestore
                const userRef = firebase.firestore().collection('users').doc(user.uid);
                await userRef.set({
                    firstName,
                    lastName,
                    nickname,
                    dob,
                    mobile,
                    email: user.email,
                    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
                }, { merge: true });

                showMessage('Profile updated successfully');

            } catch (error) {
                console.error('Error updating profile:', error);
                if (error.code === 'permission-denied') {
                    showMessage('You do not have permission to update this profile', 'error');
                } else {
                    showMessage(error.message || 'Error updating profile', 'error');
                }
            } finally {
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save Changes';
            }
        });
    }

    // Authentication state observer
    firebase.auth().onAuthStateChanged((user) => {
        if (user) {
            loadUserProfile(user);
        } else {
            window.location.href = '/login';
        }
    });

    // Logout handler
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await firebase.auth().signOut();
                window.location.href = '/login';
            } catch (error) {
                console.error('Logout error:', error);
                showMessage('Error logging out', 'error');
            }
        });
    }
}); 