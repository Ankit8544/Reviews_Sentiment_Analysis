FROM python:3.9-slim

# Install system dependencies and Chrome
RUN apt-get update && \
    apt-get install -y wget gnupg unzip && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=112.0.5615.49 && \
    wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Copy and run setup script to install additional Chrome dependencies
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh && /setup.sh

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies and suppress the warning about root user
RUN pip install -r requirements.txt --root-user-action=ignore

# Copy the application code
COPY . /app

# Expose port 5000
EXPOSE 5000

# Start the app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "600", "app:app"]

