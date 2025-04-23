#!/usr/bin/env python3
import os
import logging
from tts_api import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define directories
DIRECTORIES = ["templates", "static", "temp_audio", "voice_samples"]

def create_directories(directories):
    """Creates directories if they don't exist."""
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Created directory: {directory}")
        except OSError as e:
            logging.error(f"Failed to create directory {directory}: {e}")
            # Consider exiting if critical directories fail to create
            # sys.exit(1)


if __name__ == "__main__":
    create_directories(DIRECTORIES)

    # Get port from environment variable (for Render)
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Using port: {port}")

    # Consider using a production WSGI server like gunicorn or uWSGI in production
    # app.run(host="0.0.0.0", port=port, debug=True) # Debug mode is unsafe for production
    try:
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logging.error(f"Application failed to start: {e}")