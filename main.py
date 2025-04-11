#!/usr/bin/env python3
import os
from tts_api import app

# Create necessary directories
directories = ["templates", "static", "temp_audio", "voice_samples"]
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Get port from environment variable (for Render)
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
