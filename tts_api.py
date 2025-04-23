from flask import Flask, request, jsonify, send_file, render_template
import asyncio
import os
import io
import logging
import base64  # Moved import here
from tts_core import TTSEngine, VOICE_MODELS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tts_api")

app = Flask(__name__)
tts_engine = TTSEngine(temp_dir="./temp_audio")

# It's generally better to use Flask's built-in app context for async operations
# rather than creating a separate event loop.  However, if tts_engine *requires*
# a separate loop, this can be re-introduced, but it's less ideal.
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', voices=VOICE_MODELS)

@app.route('/api/voices', methods=['GET'])
def get_voices():
    """Return a list of available voices"""
    return jsonify({
        "success": True,
        "voices": VOICE_MODELS  # Directly return the dictionary
    })

@app.route('/api/tts', methods=['POST'])
async def text_to_speech():
    """Convert text to speech and return audio file"""
    data = request.get_json()  # Use get_json() for better error handling

    if not data or 'text' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required parameter: text"
        }), 400

    text = data['text']
    voice = data.get('voice')  # Optional parameter

    try:
        audio_data = await tts_engine.generate_audio(text, voice)

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

    except Exception as e:
        logger.exception("Error in /api/tts")  # Log the full exception traceback
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/tts/base64', methods=['POST'])
async def text_to_speech_base64():
    """Convert text to speech and return base64 encoded audio"""

    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required parameter: text"
        }), 400

    text = data['text']
    voice = data.get('voice')  # Optional parameter

    try:
        audio_data = await tts_engine.generate_audio(text, voice)

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

    except Exception as e:
        logger.exception("Error in /api/tts/base64")  # Log the full exception traceback
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/speak', methods=['POST'])
async def speak():
    """Play audio on the server (for testing purposes)"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required parameter: text"
        }), 400

    text = data['text']
    voice = data.get('voice')  # Optional parameter

    try:
        success = await tts_engine.speak_text(text, voice)

        if not success:
            return jsonify({
                "success": False,
                "error": "Failed to generate or play audio"
            }), 500

        return jsonify({
            "success": True,
            "message": "Audio played successfully"
        })

    except Exception as e:
        logger.exception("Error in /api/speak")  # Log the full exception traceback
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def server_error(e):
    logger.exception("Internal Server Error") # Log the full exception traceback
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