#!/usr/bin/env python3
import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define directories
DIRECTORIES = ["templates", "static", "temp_audio", "voice_samples"]


def create_directories(directories):
    """Creates directories if they don't exist."""
    for directory in directories:
        path = Path(directory)
        try:
            path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created directory: {directory}")
        except OSError as e:
            logging.error(f"Error creating directory {directory}: {e}")
            logging.error("The program will now exit.")
            sys.exit(1)  # Exit the program if directory creation fails


def main():
    """Main function to run the Flask app."""
    try:
        # Import the Flask app (moved inside main to avoid circular import issues)
        from tts_api import app

        create_directories(DIRECTORIES)

        # Get configuration values from environment variables
        port = int(os.environ.get("PORT", 5000))
        host = os.environ.get("HOST", "0.0.0.0")  # Default host
        flask_debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

        # Consider using a more robust configuration management solution for larger projects
        # such as using a dedicated configuration file or a library like `configparser`.

        logging.info(f"Starting app on {host}:{port} in {'debug' if flask_debug else 'production'} mode.")
        app.run(host=host, port=port, debug=flask_debug)

    except ImportError as e:
        logging.critical(f"Failed to import tts_api: {e}")
        logging.critical("The program will now exit.")
        sys.exit(1)
    except Exception as e:
        logging.exception("Application failed to start.") # Logs the full exception, including traceback
        logging.critical("The program will now exit.")
        sys.exit(1)


if __name__ == "__main__":
    main()