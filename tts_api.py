from flask import Flask, request, jsonify, send_file, render_template
import asyncio
import os
import io
import logging
import base64
from tts_core import TTSEngine, VOICE_MODELS
from functools import wraps
from typing import Optional, Tuple
from werkzeug.exceptions import BadRequest, InternalServerError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tts_api")

app = Flask(__name__)
tts_engine = TTSEngine(temp_dir="./temp_audio")


# Decorator for handling exceptions in async routes
def handle_exceptions(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {f.__name__}")
            # Consider returning a more generic error message for security
            return jsonify({
                "success": False,
                "error": "An unexpected error occurred."
            }), 500
    return wrapper


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', voices=VOICE_MODELS)


@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Return a list of available voices"""
    return jsonify({
        "success": True,
        "voices": VOICE_MODELS
    })


def validate_tts_request(data: dict) -> Optional[Tuple[str, int]]:
    """Validates the TTS request data."""
    if not data or 'text' not in data:
        return "Missing required parameter: text", 400
    if not isinstance(data['text'], str):
        return "Text must be a string", 400
    return None


@app.route('/api/tts', methods=['POST'])
@handle_exceptions
async def text_to_speech():
    """Convert text to speech and return audio file"""
    data = request.get_json()

    validation_error = validate_tts_request(data)
    if validation_error:
        error_message, status_code = validation_error
        return jsonify({
            "success": False,
            "error": error_message
        }), status_code

    text = data['text']
    voice = data.get('voice')

    try:
        audio_data = await tts_engine.generate_audio(text, voice)
    except Exception as e:
        logger.exception("Error generating audio")
        raise InternalServerError("Failed to generate audio") from e

    if not audio_data:
        return jsonify({
            "success": False,
            "error": "Failed to generate audio"
        }), 500

    audio_io = io.BytesIO(audio_data)
    audio_io.seek(0)

    return send_file(
        audio_io,
        mimetype='audio/wav',
        as_attachment=True,
        download_name='tts_audio.wav'
    )


@app.route('/api/tts/base64', methods=['POST'])
@handle_exceptions
async def text_to_speech_base64():
    """Convert text to speech and return base64 encoded audio"""

    data = request.get_json()

    validation_error = validate_tts_request(data)
    if validation_error:
        error_message, status_code = validation_error
        return jsonify({
            "success": False,
            "error": error_message
        }), status_code

    text = data['text']
    voice = data.get('voice')

    try:
        audio_data = await tts_engine.generate_audio(text, voice)
    except Exception as e:
        logger.exception("Error generating audio")
        raise InternalServerError("Failed to generate audio") from e

    if not audio_data:
        return jsonify({
            "success": False,
            "error": "Failed to generate audio"
        }), 500

    base64_audio = base64.b64encode(audio_data).decode('utf-8')

    return jsonify({
        "success": True,
        "audio_data": base64_audio,
        "voice": voice or tts_engine.default_voice
    })


@app.route('/api/speak', methods=['POST'])
@handle_exceptions
async def speak():
    """Play audio on the server (for testing purposes)"""
    data = request.get_json()

    validation_error = validate_tts_request(data)
    if validation_error:
        error_message, status_code = validation_error
        return jsonify({
            "success": False,
            "error": error_message
        }), status_code

    text = data['text']
    voice = data.get('voice')

    try:
        success = await tts_engine.speak_text(text, voice)
    except Exception as e:
        logger.exception("Error speaking text")
        raise InternalServerError("Failed to generate or play audio") from e

    if not success:
        return jsonify({
            "success": False,
            "error": "Failed to generate or play audio"
        }), 500

    return jsonify({
        "success": True,
        "message": "Audio played successfully"
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def server_error(e):
    logger.exception("Internal Server Error")
    # Consider returning a more generic error message for security
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Ensure temp directory exists
    os.makedirs('./temp_audio', exist_ok=True)

    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)