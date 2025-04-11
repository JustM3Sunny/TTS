FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for pygame
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p templates static temp_audio voice_samples

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "deploy.py", "--host", "0.0.0.0", "--port", "5000"]
