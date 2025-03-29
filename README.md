# Travel Expense Estimator

A web application that helps users estimate travel costs using machine learning and provides travel recommendations.

## Features

- User authentication with email and phone verification
- Travel cost estimation using machine learning
- Travel history tracking
- Secure HTTPS connection
- Email and SMS notifications
- Modern UI with Bootstrap 5

## Prerequisites

- Python 3.9 or higher
- Firebase project with Authentication and Firestore enabled
- Twilio account for SMS verification
- Gmail account for email verification

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd travel/src
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your credentials in the `.env` file:
     - `SECRET_KEY`: A secure random string
     - `SMTP_USERNAME`: Your Gmail address
     - `SMTP_PASSWORD`: Your Gmail app-specific password
     - `TWILIO_ACCOUNT_SID`: Your Twilio account SID
     - `TWILIO_AUTH_TOKEN`: Your Twilio auth token
     - `TWILIO_PHONE_NUMBER`: Your Twilio phone number
     - `FIREBASE_CREDENTIALS`: Your Firebase service account credentials JSON

5. Generate SSL certificates:
```bash
mkdir certificates
openssl req -x509 -newkey rsa:4096 -nodes -out certificates/certificate.crt -keyout certificates/private.key -days 365
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
https://localhost:5000
```

## Testing

Run the test suite:
```bash
pytest
```

## Deployment

The application can be deployed to various platforms:

### Heroku
1. Create a new Heroku app
2. Add the Python buildpack
3. Set environment variables in Heroku dashboard
4. Deploy using Git:
```bash
git push heroku main
```

### DigitalOcean
1. Create a new Droplet
2. Install Docker
3. Build and run the Docker container:
```bash
docker build -t travel-app .
docker run -p 5000:5000 travel-app
```

### Render
1. Create a new Web Service
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy automatically

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 