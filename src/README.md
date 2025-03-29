# Travel Cost Calculator

A web application for calculating travel costs with user authentication and verification.

## Features

- User authentication with email and Google Sign-in
- Email and SMS verification
- Travel cost calculation
- Secure HTTPS connections
- Responsive design

## Deployment to Render

### Prerequisites

1. A Render.com account (free tier available)
2. Git installed on your local machine
3. A GitHub repository for your code

### Steps to Deploy

1. **Create a Render Account**
   - Go to [Render.com](https://render.com)
   - Sign up for a free account
   - Connect your GitHub account

2. **Create a New Web Service**
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Select the repository and branch to deploy
   - Configure the service:
     - Name: `travel-calculator`
     - Environment: `Python`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app`

3. **Configure Environment Variables**
   In the Render dashboard, add the following environment variables:
   - `SECRET_KEY`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your application
   - You'll get a URL like `https://travel-calculator.onrender.com`

### Automatic Deployments

- Render automatically deploys when you push to your main branch
- You can view deployment logs in the Render dashboard
- Rollbacks are available if needed

## Local Development

1. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Generate SSL certificates**
   ```bash
   python generate_cert.py
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open https://localhost:5000 in your browser
   - Note: You'll need to accept the self-signed certificate

## Security Notes

- The application uses HTTPS for secure communication
- Environment variables are used for sensitive data
- User passwords are hashed before storage
- Email and SMS verification are implemented for additional security

## Free Tier Limitations

- 512 MB RAM
- Shared CPU
- 750 hours of runtime per month
- Automatic HTTPS
- Automatic deployments from Git

## Support

For support, please open an issue in the GitHub repository. 