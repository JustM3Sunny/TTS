#!/usr/bin/env python3
import os
import logging
import sys
from tts_api import app  # Assuming tts_api is a module/package
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)  # Get a specific logger for this module


# Define directories
DIRECTORIES = ["templates", "static", "temp_audio", "voice_samples"]


def create_directories(directories):
    """Creates directories if they don't exist. Exits if critical directories fail to create."""
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except OSError as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            logger.critical("Failed to create a critical directory. Exiting.")
            sys.exit(1)  # Exit if directory creation fails


if __name__ == "__main__":
    create_directories(DIRECTORIES)

    # Get port from environment variable (for Render)
    port = os.environ.get("PORT", "5000")  # Provide a default value as a string
    try:
        port = int(port)
    except ValueError:
        logger.warning(f"Invalid port value: {port}.  Using default port 5000.")
        port = 5000

    logger.info(f"Using port: {port}")

    # Production WSGI server like gunicorn or uWSGI is recommended
    # For development, we can use the built-in Flask server
    flask_debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("true", "1", "t")
    flask_host = os.environ.get("FLASK_HOST", "0.0.0.0")

    try:
        # Consider using a configuration file for app settings
        app.run(host=flask_host, port=port, debug=flask_debug)  # Enable debug mode based on env variable
    except Exception as e:
        logger.exception("Application failed to start.") # Log the full exception traceback
        sys.exit(1)