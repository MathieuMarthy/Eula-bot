# Use official lightweight Python image
FROM python:3.13-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to optimize Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code into the container
COPY . .

# Create non-root user for security and set up permissions
RUN useradd -m -u 1000 botuser && \
    mkdir -p /app/logs && \
    chown -R botuser:botuser /app && \
    chmod -R 755 /app/logs && \
    mkdir -p /app/tmp && \
    chmod -R 777 /app/tmp
USER botuser

# Default environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command to start the bot
CMD ["python", "main.py"]
