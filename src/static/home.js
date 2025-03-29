// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const userName = document.getElementById('userName');
    const logoutBtn = document.getElementById('logoutBtn');
    const newsletterForm = document.getElementById('newsletterForm');

    // Check authentication state for home page functionality
    auth.onAuthStateChanged(user => {
        if (user) {
            // User is signed in - update UI
            if (logoutBtn) logoutBtn.style.display = 'block';
            if (userName) {
                db.collection('users').doc(user.uid).get().then(doc => {
                    if (doc.exists()) {
                        userName.textContent = `Welcome, ${doc.data().name}`;
                    }
                });
            }
        } else {
            // User is signed out - redirect to login
            window.location.href = '/login';
        }
    });

    // Logout handler
    logoutBtn.addEventListener('click', async () => {
        try {
            await auth.signOut();
            window.location.href = '/login';
        } catch (error) {
            alert('Error signing out: ' + error.message);
        }
    });

    // Newsletter subscription handler
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = newsletterForm.querySelector('input[type="email"]').value;

            try {
                await db.collection('newsletter_subscribers').add({
                    email: email,
                    subscribedAt: firebase.firestore.FieldValue.serverTimestamp()
                });
                alert('Thank you for subscribing to our newsletter!');
                newsletterForm.reset();
            } catch (error) {
                alert('Error subscribing to newsletter: ' + error.message);
            }
        });
    }

    // Scroll animation
    function handleScrollAnimation() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            const isVisible = (elementTop < window.innerHeight) && (elementBottom >= 0);
            if (isVisible) {
                element.classList.add('visible');
            }
        });
    }

    // Initial check for elements in view
    handleScrollAnimation();

    // Check for elements in view on scroll
    window.addEventListener('scroll', handleScrollAnimation);
});

// Smooth Scroll for Navigation Links
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

// Add animation on scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.destination-card, .feature-card, .tip-card');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementBottom = element.getBoundingClientRect().bottom;
        
        if (elementTop < window.innerHeight && elementBottom > 0) {
            element.classList.add('animate');
        }
    });
};

window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll); 