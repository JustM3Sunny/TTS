#!/usr/bin/env python3
import os

# Create necessary directories
directories = ["templates", "static", "temp_audio", "voice_samples"]
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Import the Flask app
from tts_api import app

if __name__ == "__main__":
    # Get port from environment variable (for Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
