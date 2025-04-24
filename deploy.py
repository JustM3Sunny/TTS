#!/usr/bin/env python3
import os
import argparse
import subprocess
import sys
import importlib.util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REQUIRED_PACKAGES = ["flask", "aiohttp", "pygame", "requests"]
DEFAULT_DIRECTORIES = ["templates", "static", "temp_audio", "voice_samples"]


def check_dependencies(packages=None):
    """Check if all required dependencies are installed"""
    if packages is None:
        packages = REQUIRED_PACKAGES
    missing_dependencies = []
    for package in packages:
        try:
            importlib.import_module(package)  # Use import_module for a more robust check
        except ImportError:
            missing_dependencies.append(package)

    if missing_dependencies:
        logging.error(f"❌ Missing dependencies: {', '.join(missing_dependencies)}")
        logging.info("Please install all dependencies with: pip install -r requirements.txt")
        return False
    else:
        logging.info("✅ All required dependencies are installed.")
        return True


def create_directories(directories=None):
    """Create necessary directories"""
    if directories is None:
        directories = DEFAULT_DIRECTORIES
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"Created directory: {directory}")
        except OSError as e:
            logging.error(f"❌ Error creating directory {directory}: {e}")
            return False
    logging.info("✅ Created necessary directories.")
    return True


def start_server(host="0.0.0.0", port=5000, debug=False):
    """Start the TTS API server"""
    if not check_dependencies():
        sys.exit(1)  # Exit if dependencies are missing

    if not create_directories():
        sys.exit(1)

    logging.info(f"Starting TTS server on http://{host}:{port}")
    logging.info("Press Ctrl+C to stop the server.")

    # Import here to ensure dependencies are checked first
    try:
        from tts_api import app
    except ImportError as e:
        logging.error(f"❌ Error importing tts_api: {e}")
        logging.info("Please ensure tts_api.py exists and is correctly configured.")
        sys.exit(1)

    # Check if running on Render or similar platform
    if 'RENDER' in os.environ:
        # Use production server
        try:
            import gunicorn.app.base

            class StandaloneApplication(gunicorn.app.base.BaseApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        if key in self.cfg.settings and value is not None:
                            self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application

            options = {
                'bind': f"{host}:{port}",
                'workers': 4,
                'accesslog': '-',
                'errorlog': '-',
                'worker_class': 'sync',
                'timeout': 120
            }

            StandaloneApplication(app, options).run()
        except ImportError:
            logging.error("Gunicorn is required to run in production. Please install it with: pip install gunicorn")
            sys.exit(1)

    else:
        # Use Flask's built-in server for development
        app.run(debug=debug, host=host, port=port)


def install_dependencies():
    """Install dependencies using pip."""
    try:
        logging.info("Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logging.info("✅ Dependencies installed.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error installing dependencies: {e}")
        return False
    except FileNotFoundError:
        logging.error("❌ requirements.txt not found. Please ensure it exists in the current directory.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech Platform Deployment Script")

    # Add arguments
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000,
                        help="Port to bind the server to (default: 5000)")
    parser.add_argument("--debug", action="store_true",
                        help="Run the server in debug mode")
    parser.add_argument("--install", action="store_true",
                        help="Install dependencies")

    args = parser.parse_args()

    if args.install:
        if not install_dependencies():
            sys.exit(1)

    start_server(args.host, args.port, args.debug)


if __name__ == "__main__":
    main()