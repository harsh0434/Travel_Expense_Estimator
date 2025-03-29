// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const calculatorForm = document.getElementById('calculatorForm');
    const resultsSection = document.getElementById('resultsSection');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const userEmail = document.getElementById('userEmail');
    const logoutBtn = document.getElementById('logoutBtn');

    // Check if required elements exist
    if (!calculatorForm || !resultsSection || !loadingSpinner || !errorMessage) {
        console.error('Required elements not found');
        return;
    }

    // Check authentication state
    auth.onAuthStateChanged((user) => {
        if (user) {
            // User is signed in
            if (userEmail) userEmail.textContent = user.email;
            
            // Check for URL parameters to pre-fill form
            const urlParams = new URLSearchParams(window.location.search);
            const destination = urlParams.get('destination');
            const days = urlParams.get('days');
            const people = urlParams.get('people');
            const travelMode = urlParams.get('travelMode');
            const budgetLevel = urlParams.get('budgetLevel');

            if (destination) calculatorForm.destination.value = destination;
            if (days) calculatorForm.days.value = days;
            if (people) calculatorForm.people.value = people;
            if (travelMode) calculatorForm.travel_mode.value = travelMode;
            if (budgetLevel) calculatorForm.budget_level.value = budgetLevel;
        } else {
            // User is signed out, redirect to login
            window.location.href = '/login';
        }
    });

    // Format currency in Indian Rupees
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    }

    // Handle form submission
    calculatorForm.addEventListener('submit', async function(e) {
        e.preventDefault(); // Prevent form from submitting normally
        
        // Show loading state
        loadingSpinner.style.display = 'block';
        errorMessage.style.display = 'none';
        resultsSection.style.display = 'none';

        try {
            // Check if user is authenticated
            const user = auth.currentUser;
            if (!user) {
                throw new Error('Please log in to calculate costs');
            }

            // Get form values
            const destination = calculatorForm.destination.value;
            const days = parseInt(calculatorForm.days.value);
            const people = parseInt(calculatorForm.people.value);
            const travelMode = calculatorForm.travel_mode.value;
            const budgetLevel = calculatorForm.budget_level.value;

            // Validate inputs
            if (!destination || !days || !people || !travelMode || !budgetLevel) {
                throw new Error('Please fill in all fields');
            }

            // Get prediction from server
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    destination,
                    days,
                    people,
                    travel_mode: travelMode,
                    budget_level: budgetLevel
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to calculate cost');
            }

            const data = await response.json();
            console.log('Server response:', data); // Debug log
            
            // Save to Firebase history
            try {
                const historyData = {
                    userId: user.uid,
                    destination: destination,
                    days: days,
                    people: people,
                    travelMode: travelMode,
                    budgetLevel: budgetLevel,
                    dailyCost: Math.round(parseFloat(data.daily_total) || 0),
                    totalCost: Math.round(parseFloat(data.total_cost) || 0),
                    timestamp: firebase.firestore.FieldValue.serverTimestamp()
                };

                console.log('Saving history data:', historyData); // Debug log

                await db.collection('travel_history').add(historyData);
            } catch (firebaseError) {
                console.error('Firebase error:', firebaseError);
                // Continue showing results even if saving to history fails
            }

            // Display results
            resultsSection.innerHTML = `
                <div class="results-content">
                    <h2 class="results-title">Your Travel Cost Estimate</h2>
                    
                    <div class="cost-cards">
                        <div class="cost-card total">
                            <h3>Total Trip Cost</h3>
                            <div class="amount">${formatCurrency(data.total_cost)}</div>
                            <div class="details">For ${people} people, ${days} days</div>
                        </div>
                        
                        <div class="cost-card per-person">
                            <h3>Cost Per Person</h3>
                            <div class="amount">${formatCurrency(data.total_cost / people)}</div>
                            <div class="details">Total cost per person</div>
                        </div>

                        <div class="cost-card daily">
                            <h3>Daily Cost</h3>
                            <div class="amount">${formatCurrency(data.daily_total)}</div>
                            <div class="details">Per person per day</div>
                        </div>
                    </div>

                    <div class="cost-breakdown">
                        <h3>Detailed Cost Breakdown</h3>
                        <div class="breakdown-grid">
                            ${Object.entries(data.predicted_costs || {}).map(([category, cost]) => `
                                <div class="breakdown-item">
                                    <span class="category">${category.replace(/_/g, ' ').toUpperCase()}</span>
                                    <span class="amount">${formatCurrency(cost)}</span>
                                    <span class="note">per person per day</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <div class="trip-details">
                        <h3>Trip Summary</h3>
                        <div class="details-grid">
                            <div class="detail-item">
                                <span class="label">Destination</span>
                                <span class="value">${destination.charAt(0).toUpperCase() + destination.slice(1)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Duration</span>
                                <span class="value">${days} days</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Travelers</span>
                                <span class="value">${people} people</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Travel Mode</span>
                                <span class="value">${travelMode.charAt(0).toUpperCase() + travelMode.slice(1)}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Budget Level</span>
                                <span class="value">${budgetLevel.charAt(0).toUpperCase() + budgetLevel.slice(1)}</span>
                            </div>
                        </div>
                    </div>

                    <div class="action-buttons">
                        <button onclick="window.print()" class="print-btn">
                            <i class="fas fa-print"></i> Print Estimate
                        </button>
                        <a href="/history" class="history-btn">
                            <i class="fas fa-history"></i> View History
                        </a>
                    </div>
                </div>
            `;

            // Add styles for the new results layout
            const style = document.createElement('style');
            style.textContent = `
                .results-content {
                    padding: 2rem;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }

                .results-title {
                    color: #1a237e;
                    text-align: center;
                    margin-bottom: 2rem;
                    font-size: 2rem;
                }

                .cost-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }

                .cost-card {
                    padding: 1.5rem;
                    border-radius: 12px;
                    text-align: center;
                    transition: transform 0.3s ease;
                }

                .cost-card:hover {
                    transform: translateY(-5px);
                }

                .cost-card.total {
                    background: linear-gradient(135deg, #1a237e, #3949ab);
                    color: white;
                }

                .cost-card.per-person {
                    background: linear-gradient(135deg, #0277bd, #039be5);
                    color: white;
                }

                .cost-card.daily {
                    background: linear-gradient(135deg, #00838f, #00acc1);
                    color: white;
                }

                .cost-card h3 {
                    font-size: 1.2rem;
                    margin-bottom: 1rem;
                    opacity: 0.9;
                }

                .cost-card .amount {
                    font-size: 2rem;
                    font-weight: 700;
                    margin-bottom: 0.5rem;
                }

                .cost-card .details {
                    font-size: 0.9rem;
                    opacity: 0.8;
                }

                .cost-breakdown {
                    background: #f8f9fa;
                    padding: 2rem;
                    border-radius: 12px;
                    margin: 2rem 0;
                }

                .cost-breakdown h3 {
                    color: #1a237e;
                    margin-bottom: 1.5rem;
                }

                .breakdown-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                }

                .breakdown-item {
                    padding: 1rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }

                .breakdown-item .category {
                    display: block;
                    color: #1a237e;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                }

                .breakdown-item .amount {
                    display: block;
                    font-size: 1.2rem;
                    color: #2196f3;
                    margin-bottom: 0.25rem;
                }

                .breakdown-item .note {
                    display: block;
                    font-size: 0.8rem;
                    color: #666;
                }

                .trip-details {
                    background: #f8f9fa;
                    padding: 2rem;
                    border-radius: 12px;
                    margin: 2rem 0;
                }

                .trip-details h3 {
                    color: #1a237e;
                    margin-bottom: 1.5rem;
                }

                .details-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                }

                .detail-item {
                    padding: 1rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }

                .detail-item .label {
                    display: block;
                    color: #666;
                    font-size: 0.9rem;
                    margin-bottom: 0.5rem;
                }

                .detail-item .value {
                    display: block;
                    color: #1a237e;
                    font-weight: 600;
                }

                .action-buttons {
                    display: flex;
                    gap: 1rem;
                    justify-content: center;
                    margin-top: 2rem;
                }

                .action-buttons button,
                .action-buttons a {
                    padding: 0.8rem 1.5rem;
                    border-radius: 25px;
                    font-weight: 600;
                    text-decoration: none;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    transition: all 0.3s ease;
                }

                .print-btn {
                    background: #1a237e;
                    color: white;
                    border: none;
                    cursor: pointer;
                }

                .history-btn {
                    background: #f5f5f5;
                    color: #1a237e;
                    border: 2px solid #1a237e;
                }

                .print-btn:hover,
                .history-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }

                @media (max-width: 768px) {
                    .cost-cards {
                        grid-template-columns: 1fr;
                    }

                    .breakdown-grid,
                    .details-grid {
                        grid-template-columns: 1fr;
                    }

                    .action-buttons {
                        flex-direction: column;
                    }
                }
            `;
            document.head.appendChild(style);

            resultsSection.style.display = 'block';
            
            // Scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = error.message || 'An error occurred. Please try again.';
            errorMessage.style.display = 'block';
        } finally {
            loadingSpinner.style.display = 'none';
        }
    });

    // Handle logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function() {
            try {
                await auth.signOut();
                window.location.href = '/login';
            } catch (error) {
                console.error('Error signing out:', error);
            }
        });
    }
}); 