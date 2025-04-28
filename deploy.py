#!/usr/bin/env python3
import os
import argparse
import subprocess
import sys
import importlib.util
import logging
import venv
import shutil
import platform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REQUIRED_PACKAGES = ["flask", "aiohttp", "pygame", "requests"]
DEFAULT_DIRECTORIES = ["templates", "static", "temp_audio", "voice_samples"]
VENV_DIR = "venv"
REQUIREMENTS_FILE = "requirements.txt"


def check_dependencies(packages=None):
    """Check if all required dependencies are installed"""
    if packages is None:
        packages = REQUIRED_PACKAGES
    missing_dependencies = []
    for package in packages:
        try:
            # Attempt to import the top-level package name only
            importlib.import_module(package.split('.')[0])
        except ImportError:
            missing_dependencies.append(package)

    if missing_dependencies:
        logging.error(f"❌ Missing dependencies: {', '.join(missing_dependencies)}")
        logging.info(f"Please install all dependencies with: pip install -r {REQUIREMENTS_FILE}")
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
        logging.error("Dependencies are missing. Exiting.")
        sys.exit(1)  # Exit if dependencies are missing

    if not create_directories():
        logging.error("Failed to create directories. Exiting.")
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
        # Use the venv's pip if a virtual environment is active
        pip_executable = [sys.executable, "-m", "pip"]
        subprocess.check_call(pip_executable + ["install", "--no-cache-dir", "-r", REQUIREMENTS_FILE])
        logging.info("✅ Dependencies installed.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error installing dependencies: {e}")
        return False
    except FileNotFoundError:
        logging.error(f"❌ {REQUIREMENTS_FILE} not found. Please ensure it exists in the current directory.")
        return False


def create_virtual_environment():
    """Creates a virtual environment."""
    try:
        logging.info(f"Creating virtual environment in {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        logging.info(f"✅ Virtual environment created in {VENV_DIR}.")
        return True
    except Exception as e:
        logging.error(f"❌ Error creating virtual environment: {e}")
        # Attempt to remove the directory if creation fails
        try:
            shutil.rmtree(VENV_DIR)
            logging.info(f"Removed partially created virtual environment directory: {VENV_DIR}")
        except OSError as remove_error:
            logging.warning(f"Failed to remove partially created virtual environment directory: {remove_error}")
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
    parser.add_argument("--venv", action="store_true",
                        help="Create a virtual environment")
    parser.add_argument("--no-check-deps", action="store_true",
                        help="Skip dependency check (useful for CI/CD or when dependencies are managed externally)")
    parser.add_argument("--no-exit", action="store_true",
                        help="Do not exit after creating venv. Useful for automation.")


    args = parser.parse_args()

    if args.venv:
        if os.path.exists(VENV_DIR):
            logging.warning(f"Virtual environment directory '{VENV_DIR}' already exists.  Please remove it or choose a different directory.")
            if not args.no_exit:
                sys.exit(1)
        if not create_virtual_environment():
            if not args.no_exit:
                sys.exit(1)
        venv_activation_command = f"source {VENV_DIR}/bin/activate" if platform.system() != "Windows" else f"{VENV_DIR}\\Scripts\\activate"
        print(f"Please activate the virtual environment using:\n{venv_activation_command}")
        if not args.no_exit:
            sys.exit(0)

    if args.install:
        if not install_dependencies():
            sys.exit(1)

    if not args.no_check_deps:
        if not check_dependencies():
            sys.exit(1)

    start_server(args.host, args.port, args.debug)


if __name__ == "__main__":
    main()