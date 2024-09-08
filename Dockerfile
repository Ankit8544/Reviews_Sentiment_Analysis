FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=1200

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    xvfb \
    gnupg \
    curl \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome browser
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN wget https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.119/win64/chromedriver-win64.zip -O /chromedriver.zip && \
    unzip /chromedriver.zip -d /chromedriver && \
    rm /chromedriver.zip && \
    mv /chromedriver/chromedriver.exe /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.org/simple

# Install NLTK packages
RUN python -m nltk.downloader punkt stopwords

# Set the display port to avoid crashes due to no display
ENV DISPLAY=:99

# Set up working directory
WORKDIR /app

# Copy the rest of the application code
COPY . /app/

# Expose the port Flask will run on
EXPOSE 5000

# Command to run your Flask app
CMD ["python", "app.py"]
