# Base image with Python and Solana CLI
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/templates

# Expose ports
EXPOSE 5000
EXPOSE 8765

# Environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Command to run the application
CMD ["python", "main.py"]
