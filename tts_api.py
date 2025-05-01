from flask import Flask, request, jsonify, send_file, render_template
import asyncio
import os
import io
import logging
import base64
from tts_core import TTSEngine, VOICE_MODELS
from functools import wraps
from typing import Optional, Tuple, Dict, Any
from werkzeug.exceptions import BadRequest, InternalServerError
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tts_api")

app = Flask(__name__)
tts_engine = TTSEngine(temp_dir="./temp_audio")

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit for requests
ALLOWED_EXTENSIONS = {'txt'}

# Thread pool for blocking operations
app.executor = ThreadPoolExecutor(max_workers=4)


# Decorator for handling exceptions in async routes
def handle_exceptions(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as e:
            error_message = f"Error in {f.__name__}: {type(e).__name__} - {str(e)}"
            logger.error(error_message, exc_info=True)  # Log with traceback
            return jsonify({
                "success": False,
                "error": error_message
            }), 500
    return wrapper


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', voices=VOICE_MODELS)


@app.route('/api/voices', methods=['GET'])
async def get_voices():
    """Return a list of available voices"""
    return jsonify({
        "success": True,
        "voices": VOICE_MODELS
    })


def validate_tts_request(data: Dict[str, Any]) -> Optional[Tuple[str, int]]:
    """Validates the TTS request data."""
    if not data or 'text' not in data:
        return "Missing required parameter: text", 400
    text = data.get('text', '')  # Use .get() to avoid KeyError
    if not isinstance(text, str):
        return "Text must be a string", 400
    text = text.strip()
    if not text:
        return "Text cannot be empty or contain only whitespace", 400
    if len(text) > 5000:  # Increased text length limit
        return "Text too long. Maximum length is 5000 characters.", 400
    return None


async def generate_audio_async(text: str, voice: Optional[str]) -> bytes:
    """Run audio generation in a thread pool to avoid blocking the event loop."""
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(app.executor, tts_engine.generate_audio, text, voice)
    except Exception as e:
        logger.error(f"Error in generate_audio_async: {e}", exc_info=True)
        raise


async def process_tts_request(data: Dict[str, Any]) -> Tuple[Optional[bytes], Optional[Tuple[str, int]]]:
    """Processes the TTS request, handling validation and audio generation."""
    validation_error = validate_tts_request(data)
    if validation_error:
        return None, validation_error

    text = data['text']
    voice = data.get('voice')

    try:
        audio_data = await generate_audio_async(text, voice)
        return audio_data, None
    except Exception as e:
        logger.exception("Error generating audio")
        return None, ("Failed to generate audio", 500)


@app.route('/api/tts', methods=['POST'])
@handle_exceptions
async def text_to_speech():
    """Convert text to speech and return audio file"""
    data = request.get_json()

    audio_data, error_info = await process_tts_request(data)

    if error_info:
        error_message, status_code = error_info
        return jsonify({
            "success": False,
            "error": error_message
        }), status_code

    if not audio_data:
        return jsonify({
            "success": False,
            "error": "Failed to generate audio"
        }), 500

    return send_file(
        io.BytesIO(audio_data),  # Directly create BytesIO object
        mimetype='audio/wav',
        as_attachment=True,
        download_name='tts_audio.wav'
    )


@app.route('/api/tts/base64', methods=['POST'])
@handle_exceptions
async def text_to_speech_base64():
    """Convert text to speech and return base64 encoded audio"""

    data = request.get_json()

    audio_data, error_info = await process_tts_request(data)

    if error_info:
        error_message, status_code = error_info
        return jsonify({
            "success": False,
            "error": error_message
        }), status_code

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
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(app.executor, tts_engine.speak_text, text, voice)
    except Exception as e:
        logger.exception("Error speaking text")
        return jsonify({
            "success": False,
            "error": "Failed to generate or play audio"
        }), 500

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
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


@app.route('/api/upload', methods=['POST'])
@handle_exceptions
async def upload_text():
    """Upload a text file and convert it to speech."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            text = (await asyncio.to_thread(file.read)).decode('utf-8')  # Read and decode in one step
        except UnicodeDecodeError:
            return jsonify({"success": False, "error": "Failed to decode file.  Please ensure it is UTF-8 encoded."}), 400

        data = {'text': text}
        audio_data, error_info = await process_tts_request(data)

        if error_info:
            error_message, status_code = error_info
            return jsonify({
                "success": False,
                "error": error_message
            }), status_code

        if not audio_data:
            return jsonify({
                "success": False,
                "error": "Failed to generate audio"
            }), 500

        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/wav',
            as_attachment=True,
            download_name='tts_audio.wav'
        )
    else:
        return jsonify({"success": False, "error": "Invalid file type. Only .txt files are allowed."}), 400


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Ensure temp directory exists
    os.makedirs('./temp_audio', exist_ok=True)

    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)