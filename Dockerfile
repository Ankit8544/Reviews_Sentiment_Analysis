FROM python:3.9-slim

# Install system dependencies and Chrome
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and run setup script to install Chrome dependencies
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh && /setup.sh

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy the application code
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Start the app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
