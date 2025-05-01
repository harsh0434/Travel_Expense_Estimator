// Initialize Firestore
const db = firebase.firestore();

// Handle estimate form submission
async function handleEstimate(event) {
    event.preventDefault();
    
    const destination = document.getElementById('destination').value;
    const duration = parseInt(document.getElementById('duration').value);
    const travelers = parseInt(document.getElementById('travelers').value);
    const accommodation = document.getElementById('accommodation').value;

    // Show loading spinner
    document.getElementById('loadingEstimate').classList.remove('d-none');
    document.getElementById('estimateResult').classList.add('d-none');

    try {
        // Get current user
        const user = firebase.auth().currentUser;
        if (!user) {
            throw new Error('User not authenticated');
        }

        // Get estimate from backend
        const response = await fetch('/estimate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                destination,
                duration,
                travelers,
                accommodation
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get estimate');
        }

        const estimate = await response.json();

        // Update UI with estimate
        document.getElementById('totalCost').textContent = `$${estimate.total.toFixed(2)}`;
        document.getElementById('accommodationCost').textContent = `$${estimate.accommodation.toFixed(2)}`;
        document.getElementById('transportationCost').textContent = `$${estimate.transportation.toFixed(2)}`;
        document.getElementById('foodCost').textContent = `$${estimate.food.toFixed(2)}`;
        document.getElementById('activitiesCost').textContent = `$${estimate.activities.toFixed(2)}`;

        // Save estimate to Firestore
        await db.collection('travel_history').add({
            userId: user.uid,
            destination,
            duration,
            travelers,
            accommodation,
            total: estimate.total,
            breakdown: {
                accommodation: estimate.accommodation,
                transportation: estimate.transportation,
                food: estimate.food,
                activities: estimate.activities
            },
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });

        // Show estimate result
        document.getElementById('estimateResult').classList.remove('d-none');
        
        // Refresh travel history
        loadTravelHistory();
    } catch (error) {
        console.error('Estimate error:', error);
        alert(error.message);
    } finally {
        // Hide loading spinner
        document.getElementById('loadingEstimate').classList.add('d-none');
    }
}

// Load travel history from Firestore
async function loadTravelHistory() {
    try {
        const user = firebase.auth().currentUser;
        if (!user) {
            throw new Error('User not authenticated');
        }

        const snapshot = await db.collection('travel_history')
            .where('userId', '==', user.uid)
            .orderBy('timestamp', 'desc')
            .limit(10)
            .get();

        const historyHtml = snapshot.docs.map(doc => {
            const data = doc.data();
            return `
                <tr>
                    <td>${data.destination}</td>
                    <td>${data.duration} days</td>
                    <td>${data.travelers}</td>
                    <td>${data.accommodation}</td>
                    <td>$${data.total.toFixed(2)}</td>
                    <td>${data.timestamp.toDate().toLocaleDateString()}</td>
                </tr>
            `;
        }).join('');

        document.getElementById('travelHistory').innerHTML = historyHtml;
    } catch (error) {
        console.error('Load history error:', error);
        alert('Failed to load travel history');
    }
}

// Load travel history when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadTravelHistory();
}); 