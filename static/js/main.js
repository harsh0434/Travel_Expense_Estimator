// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Travel cost estimation
async function estimateTravelCost(event) {
    event.preventDefault();
    
    if (!validateForm('travelForm')) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }

    const formData = {
        destination: document.getElementById('destination').value,
        duration: parseInt(document.getElementById('duration').value),
        season: document.getElementById('season').value,
        accommodation_type: document.getElementById('accommodation_type').value
    };

    try {
        const response = await fetch('/estimate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert(`Estimated cost: $${data.estimated_cost.toFixed(2)}`, 'success');
            updateCostChart(data.estimated_cost);
        } else {
            showAlert(data.error || 'Error estimating cost', 'danger');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'danger');
        console.error('Error:', error);
    }
}

// Travel recommendations
async function getRecommendations(event) {
    event.preventDefault();
    
    if (!validateForm('recommendationsForm')) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }

    const formData = {
        preferences: document.getElementById('preferences').value,
        budget: parseFloat(document.getElementById('budget').value)
    };

    try {
        const response = await fetch('/get_recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        
        if (data.success) {
            displayRecommendations(data.recommendations);
        } else {
            showAlert(data.error || 'Error getting recommendations', 'danger');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'danger');
        console.error('Error:', error);
    }
}

// Display recommendations
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');
    if (!container) return;

    container.innerHTML = recommendations.map(rec => `
        <div class="recommendation-card">
            <h3>${rec.name}</h3>
            <p>${rec.description}</p>
            <p>Estimated Cost: $${rec.cost.toFixed(2)}</p>
            <button class="btn btn-primary" onclick="selectDestination('${rec.name}')">
                Select Destination
            </button>
        </div>
    `).join('');
}

// Show alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Update cost chart
function updateCostChart(cost) {
    const chart = document.getElementById('costChart');
    if (!chart) return;

    // Update chart with new cost
    // This is a placeholder for chart.js implementation
}

// Select destination
function selectDestination(destination) {
    document.getElementById('destination').value = destination;
    showAlert(`Selected destination: ${destination}`, 'success');
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 