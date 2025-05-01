// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
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
            if (user.email && userEmail) {
                userEmail.textContent = user.email;
            }
        } else {
            window.location.href = '/login';
        }
    });

    // Logout handler
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            firebase.auth().signOut()
                .then(() => {
                    window.location.href = '/login';
                })
                .catch((error) => {
                    console.error('Logout error:', error);
                });
        });
    }

    // Helper function to format currency
    function formatCurrency(amount) {
        return '₹' + amount.toLocaleString('en-IN');
    }

    // Form submission handler
    if (calculatorForm) {
        calculatorForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Get form data
            const formData = {
                destination: document.getElementById('destination').value,
                days: parseInt(document.getElementById('days').value),
                people: parseInt(document.getElementById('people').value),
                travelMode: document.getElementById('travelMode').value,
                budgetLevel: document.getElementById('budgetLevel').value
            };

            // Validate form data
            if (!formData.destination || !formData.days || !formData.people || !formData.travelMode || !formData.budgetLevel) {
                alert('Please fill in all fields');
                return;
            }

            // Disable the submit button to prevent double submission
            const submitButton = calculatorForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.textContent = 'Calculating...';

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        destination: formData.destination,
                        days: formData.days,
                        people: formData.people,
                        travel_mode: formData.travelMode,
                        budget_level: formData.budgetLevel
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to calculate costs');
                }

                const data = await response.json();
                
                // Update the UI with the results
                if (accommodationCost) accommodationCost.textContent = formatCurrency(data.predicted_costs.accommodation);
                if (foodCost) foodCost.textContent = formatCurrency(data.predicted_costs.food);
                if (activitiesCost) activitiesCost.textContent = formatCurrency(data.predicted_costs.activities);
                if (transportCost) transportCost.textContent = formatCurrency(data.predicted_costs.transport);
                
                // Calculate and display total cost
                const total = data.total_cost;
                if (totalCost) totalCost.textContent = formatCurrency(total);
                if (tripSummary) tripSummary.textContent = `${formData.people} ${formData.people > 1 ? 'people' : 'person'} for ${formData.days} ${formData.days > 1 ? 'days' : 'day'}`;

                // Show the results section with animation
                if (resultsSection) {
                    resultsSection.classList.add('show');
                    resultsSection.scrollIntoView({ behavior: 'smooth' });
                }

            } catch (error) {
                console.error('Error:', error);
                alert(error.message || 'Error calculating travel costs. Please try again.');
            } finally {
                // Re-enable the submit button
                const submitButton = calculatorForm.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Calculate Cost';
                }
            }
        });
    }
}); 