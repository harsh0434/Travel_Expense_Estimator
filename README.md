# TravelMint Travel Cost Calculator

A modern web application that helps travelers estimate their trip costs to various destinations in India. The application uses machine learning to provide accurate cost predictions based on multiple factors including destination, duration, group size, travel mode, and budget level.

## 🌟 Features

- **Smart Cost Prediction**: ML-powered travel cost estimation
- **User Authentication**: Secure Firebase-based authentication
- **Interactive UI**: Modern, responsive design with animations
- **Detailed Breakdown**: Category-wise cost analysis
- **Multiple Destinations**: Support for major Indian tourist spots
- **Budget Flexibility**: Options for different budget levels

## 🏗️ Project Structure
```
travel/
├── src/
│   ├── static/
│   │   ├── calculator.js    # Calculator functionality
│   │   ├── home.js         # Home page interactions
│   │   ├── auth.js         # Authentication handling
│   │   └── styles.css      # Global styles
│   ├── templates/
│   │   ├── home.html       # Home page template
│   │   ├── calculator.html # Calculator page template
│   │   └── login.html      # Login page template
│   ├── app.py             # Flask application
│   └── predict.py         # ML prediction logic
├── data/
│   └── travel_costs.json  # Training data
└── models/
    ├── travel_cost_model.joblib  # Trained ML model
    └── encoders.joblib           # Feature encoders
```

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3 with modern features
- JavaScript (ES6+)
- Font Awesome icons
- Google Fonts (Poppins)
- Unsplash images

### Backend
- Python Flask
- scikit-learn
- NumPy
- joblib

### Authentication
- Firebase Authentication
- Email/Password login
- Session management

## 💻 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/incredible-india-travel.git
   cd incredible-india-travel
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Firebase**
   - Create a Firebase project
   - Enable Email/Password authentication
   - Add your Firebase config to `static/auth.js`

5. **Run the Application**
   ```bash
   cd src
   python app.py
   ```

6. **Access the Application**
   - Open http://127.0.0.1:5000 in your browser

## 🔧 Key Components

### Home Page
- Modern navigation bar with blur effect
- Full-screen hero section
- Animated destination cards
- Feature highlights
- Call-to-action sections

### Calculator Page
- Interactive form with validation
- Real-time cost calculations
- Animated results display
- Detailed cost breakdown
- Category-wise analysis

### Prediction System
```python
class TravelCostPredictor:
    # Base costs for different budget levels
    base_costs = {
        'low': {
            'accommodation': 800,   # Budget hotels/hostels
            'food': 400,           # Local restaurants
            'activities': 300,     # Basic sightseeing
            'transport': {...}     # Various modes
        },
        'mid': {...},
        'high': {...}
    }
    
    # Region-specific multipliers
    region_multipliers = {
        'north india': 1.1,
        'south india': 1.1,
        'east india': 1.0,
        'west india': 1.2,
        'central india': 1.0,
        'northeast india': 1.2
    }
```

## 🔐 Security Features

- Firebase Authentication integration
- Protected routes
- Input validation
- CSRF protection
- Secure API calls
- Error handling

## 📱 Responsive Design

- Mobile-first approach
- Flexible grid systems
- Adaptive layouts
- Touch-friendly interactions
- Responsive typography

## ⚡ Performance Optimizations

- Lazy loading for images
- Minified resources
- Efficient animations
- Cached predictions
- Optimized API calls

## 🔄 User Flow

1. User Authentication
   - Login/Signup via Firebase
   - Email verification (optional)

2. Home Page Navigation
   - Browse destinations
   - View features
   - Access calculator

3. Cost Calculation
   - Input travel details
   - Select preferences
   - View cost breakdown
   - Modify inputs as needed

## 💰 Cost Calculation Process

1. **Base Cost Selection**
   - Budget-friendly options
   - Moderate comfort level
   - Luxury experience

2. **Multiplier Application**
   - Region-specific adjustments
   - Destination factors
   - Seasonal variations

3. **Final Calculations**
   - Per person per day costs
   - Total trip cost
   - Category-wise breakdown

## 🚀 Future Enhancements

- [ ] Additional destinations
- [ ] More travel modes
- [ ] Seasonal pricing
- [ ] Hotel recommendations
- [ ] Activity suggestions
- [ ] Trip planning features

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- Your Name - Initial work - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Firebase for authentication
- Unsplash for images
- Font Awesome for icons
- Google Fonts for typography

## 📞 Support

For support, email your@email.com or create an issue in the repository. 