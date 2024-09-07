# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install system dependencies for Chrome and utilities
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    google-chrome-stable \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set the display port for headless Chrome
ENV DISPLAY=:99

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose the port on which the Flask app will run
EXPOSE 5000

# Define the command to run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
