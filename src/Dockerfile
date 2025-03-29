# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Generate SSL certificates
RUN python generate_cert.py

# Expose port
ENV PORT=5000
EXPOSE $PORT

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application with SSL
CMD ["gunicorn", "--certfile=certificates/certificate.crt", "--keyfile=certificates/private.key", "--bind=0.0.0.0:$PORT", "--workers=2", "--timeout=120", "app:app"] 