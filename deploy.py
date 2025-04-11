#!/usr/bin/env python3
import os
import argparse
import subprocess
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import aiohttp
        import pygame
        import requests
        print("✅ All required dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("Please install all dependencies with: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["templates", "static", "temp_audio", "voice_samples"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Created necessary directories.")

def start_server(host="0.0.0.0", port=5000, debug=False):
    """Start the TTS API server"""
    if not check_dependencies():
        return

    create_directories()

    print(f"Starting TTS server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server.")

    # Import here to ensure dependencies are checked first
    from tts_api import app

    # Check if running on Render or similar platform
    if 'RENDER' in os.environ:
        # Use production server
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
    else:
        # Use Flask's built-in server for development
        app.run(debug=debug, host=host, port=port)

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
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed.")

    start_server(args.host, args.port, args.debug)

if __name__ == "__main__":
    main()
