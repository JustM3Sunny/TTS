#!/usr/bin/env python3
import os
import logging
import sys
from pathlib import Path

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
            sys.exit(1)  # Exit the program if directory creation fails


def main():
    """Main function to run the Flask app."""
    try:
        create_directories(DIRECTORIES)

        # Import the Flask app (moved inside main to avoid circular import issues)
        from tts_api import app

        # Get port from environment variable (for Render)
        port = int(os.environ.get("PORT", 5000))
        logging.info(f"Starting app on port: {port}")
        # Consider using a configuration object or environment variables for host
        app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "False") == "True")
    except ImportError as e:
        logging.critical(f"Failed to import tts_api: {e}")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()