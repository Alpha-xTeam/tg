# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies (ffmpeg, wget, Chrome for Selenium)
RUN apt-get update && apt-get install -y ffmpeg wget gnupg curl && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies and yt-dlp
RUN pip install --no-cache-dir -r requirements.txt yt-dlp

# Copy the rest of the application code
COPY . .

# Ensure the app directory is writable
RUN chmod -R 777 /app

# Environment variables will be read from the host or .env file
# Ensure logs are visible in docker logs
ENV PYTHONUNBUFFERED=1

# Create downloads directory to avoid permission issues
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# Command to run the bot
CMD ["python", "bot.py"]
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot.py"]
