FROM python:3.11-slim

# Install Chrome, ChromeDriver and other dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    xvfb \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libnss3 \
    libglib2.0-0 \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN python -m pip install --upgrade pip
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps

# Set up virtual display
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Create downloads directory
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure the application files are owned by the non-root user
RUN chmod -R 755 /app

# Expose the port the app runs on
EXPOSE 5000

# Use environment variables for configuration
ENV PORT=5000

# Command to run the application with Gunicorn (more reliable than Flask's dev server)
CMD gunicorn --bind 0.0.0.0:$PORT app:app