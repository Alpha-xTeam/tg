# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies (ffmpeg for audio conversion, wget)
RUN apt-get update && apt-get install -y ffmpeg wget && \
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
RUN chmod -R 777 /app && mkdir -p /app/downloads && chmod 777 /app/downloads

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the bot
CMD ["python", "bot.py"]
