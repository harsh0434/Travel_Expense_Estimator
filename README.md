# TravelMint Travel Cost Calculator

A modern web application that helps travelers estimate their trip costs to various destinations in India. The application uses machine learning to provide accurate cost predictions based on multiple factors including destination, duration, group size, travel mode, and budget level.

## 🌟 Features

- **Smart Cost Prediction**: ML-powered travel cost estimation
- **User Authentication**: Secure Firebase-based authentication (frontend) and session management (backend)
- **Interactive UI**: Modern, responsive design with animations
- **Detailed Breakdown**: Category-wise cost analysis
- **Multiple Destinations**: Support for major Indian tourist spots
- **Budget Flexibility**: Options for different budget levels

## 🏗️ Project Structure
```
travel/
├── src/
│   ├── static/
│   │   ├── calculator.js    # Calculator functionality (frontend logic)
│   │   ├── home.js         # Home page interactions
│   │   ├── auth.js         # Authentication handling (Firebase Auth, session)
│   │   ├── styles.css      # Global styles
│   │   ├── calculator.css  # Calculator page styles
│   │   ├── home.css        # Home page styles
│   │   ├── auth.css        # Auth page styles
│   │   ├── profile.js      # Profile page logic
│   │   └── images/         # Static images
│   ├── templates/
│   │   ├── home.html       # Home page template
│   │   ├── calculator.html # Calculator page template
│   │   ├── profile.html    # Profile page template
│   │   └── login.html      # Login page template
│   ├── app.py             # Flask application (backend, API, session)
│   ├── predict.py         # ML prediction logic
│   ├── travel_calculator.py # Additional backend logic
│   ├── train_model.py     # Model training script
│   └── test_app.py        # Backend tests
├── models/                # Trained ML models (created after training)
├── data/                  # Training data (created after training)
├── firebase-adminsdk.json # Firebase Admin SDK credentials (backend auth)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── ...
```

## 🛠️ Technologies Used

### Frontend
- HTML5, CSS3 (with custom styles for each page)
- JavaScript (ES6+)
- Firebase Authentication (Email/Password, Google, Phone)
- Font Awesome, Google Fonts

### Backend
- Python Flask (web server, API, session management)
- scikit-learn, joblib, numpy (ML prediction)
- firebase-admin (verifies Firebase tokens, manages sessions)

### Authentication
- **Frontend**: `src/static/auth.js` uses Firebase Auth for login/signup, gets ID token
- **Backend**: `src/app.py` verifies ID token using Firebase Admin SDK, creates Flask session
- **Session**: Flask session is used to protect routes and maintain login state

## 🔄 Project Flow

1. **User visits the site**
   - If not authenticated, redirected to `/login` (handled by Flask and JS)
2. **Login/Signup**
   - User logs in via Firebase Auth (frontend, `auth.js`)
   - On success, frontend gets Firebase ID token and sends it to `/login` (Flask backend)
   - Flask verifies token with Firebase Admin SDK, creates session
3. **Session Management**
   - Flask session stores user ID and email
   - Protected routes (`/home`, `/calculator`, `/profile`) require session
   - Logout clears session and signs out from Firebase
4. **Home Page**
   - User sees destinations, features, and navigation
5. **Calculator Page**
   - User enters trip details
   - Frontend sends data to `/predict` API (Flask)
   - Flask uses ML model to predict costs and returns breakdown
   - Results are displayed interactively
6. **Profile Page**
   - User can view/edit profile (future enhancement)

## 💻 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd travel
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install firebase-admin
   ```

4. **Set Up Firebase**
   - Create a Firebase project
   - Enable Email/Password, Google, and Phone authentication
   - Download your service account key as `firebase-adminsdk.json` and place it in the project root
   - Add your Firebase config to `src/static/auth.js`

5. **Train the Model (Optional)**
   - Place your training data in `data/`
   - Run `python src/train_model.py` to generate model files in `models/`

6. **Run the Application**
   ```bash
   cd src
   python app.py
   ```

7. **Access the Application**
   - Open http://127.0.0.1:5000 in your browser

## 🔐 Security Features
- Firebase Authentication integration (frontend & backend)
- Protected routes (Flask session)
- Input validation (frontend & backend)
- Secure API calls (token verification)
- Error handling and logging

## 📁 Where Each Technology is Used
- **Flask**: `src/app.py` (routes, API, session), `src/predict.py` (ML logic)
- **Firebase Auth**: `src/static/auth.js` (login/signup, token), `src/app.py` (token verification)
- **ML Model**: `src/predict.py`, `models/` (trained model files)
- **Frontend**: `src/static/` (JS, CSS), `src/templates/` (HTML)

## 🚦 How Authentication Works
- User logs in via Firebase Auth (frontend)
- JS gets ID token and sends to Flask `/login`
- Flask verifies token with Firebase Admin SDK
- On success, Flask creates session and user can access protected pages
- Logout clears both Firebase and Flask session

## 💡 How Prediction Works
- User fills calculator form
- Frontend sends data to `/predict` (Flask)
- Flask loads ML model, predicts costs, returns JSON
- Frontend displays results

## 🚀 Future Enhancements
- [ ] Additional destinations
- [ ] More travel modes
- [ ] Seasonal pricing
- [ ] Hotel recommendations
- [ ] Activity suggestions
- [ ] Trip planning features

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
[MIT](LICENSE)

## 👥 Authors

- Your Name - Initial work - [YourGitHub](https://github.com/harsh0434/TravelMint.git)

## 🙏 Acknowledgments

- Firebase for authentication
- Unsplash for images
- Font Awesome for icons
- Google Fonts for typography

## 📞 Support

For support, email your@email.com or create an issue in the repository.
