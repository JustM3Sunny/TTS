# Advanced Text-to-Speech Platform

A powerful and flexible text-to-speech platform that uses the Deepgram API to convert text to speech with multiple voice options.

## Features

- Support for 12 different voices
- Web interface for easy testing and usage
- REST API for integration with other applications
- Python client library for easy integration in Python projects
- Command-line interface for quick text-to-speech conversion

## Available Voices

- Asteria (aura-asteria-en)
- Orpheus (aura-orpheus-en)
- Angus (aura-angus-en)
- Arcas (aura-arcas-en)
- Athena (aura-athena-en)
- Helios (aura-helios-en)
- Hera (aura-hera-en)
- Luna (aura-luna-en)
- Orion (aura-orion-en)
- Perseus (aura-perseus-en)
- Stella (aura-stella-en)
- Zeus (aura-zeus-en)

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd text-to-speech-platform
```

2. Install the required dependencies:
```
pip install flask aiohttp pygame
```

## Usage

### Web Interface

1. Start the web server:
```
python tts_api.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter text, select a voice, and click "Generate Speech" to convert text to speech.

### Command-Line Interface

Convert text to speech and play it:
```
python tts_cli.py --text "Hello, this is a test." --voice "Asteria"
```

Convert text from a file to speech and save it to an audio file:
```
python tts_cli.py --file input.txt --voice "Zeus" --output output.wav
```

List available voices:
```
python tts_cli.py --list-voices
```

### Python Client Library

```python
import asyncio
from tts_client import TTSClient

async def example():
    client = TTSClient()
    
    # Get available voices
    voices = await client.get_available_voices()
    print(voices)
    
    # Convert text to speech and save to file
    success = await client.save_audio_file(
        "Hello, this is a test.",
        "output.wav",
        "Asteria"
    )
    
    print(f"Success: {success}")

# Run the example
asyncio.run(example())
```

### REST API

#### Get Available Voices

```
GET /api/voices
```

Response:
```json
{
    "success": true,
    "voices": {
        "Asteria": "aura-asteria-en",
        "Orpheus": "aura-orpheus-en",
        ...
    }
}
```

#### Convert Text to Speech (Audio File)

```
POST /api/tts
Content-Type: application/json

{
    "text": "Your text to convert to speech",
    "voice": "Asteria"
}
```

Response: Audio file (WAV format)

#### Convert Text to Speech (Base64)

```
POST /api/tts/base64
Content-Type: application/json

{
    "text": "Your text to convert to speech",
    "voice": "Asteria"
}
```

Response:
```json
{
    "success": true,
    "audio_data": "base64_encoded_audio_data",
    "voice": "Asteria"
}
```

## Integration Examples

### JavaScript

```javascript
async function convertTextToSpeech() {
    const response = await fetch('http://localhost:5000/api/tts/base64', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: "Hello, this is a test of the text to speech API.",
            voice: "Asteria"
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Create audio from base64 data
        const audio = new Audio(`data:audio/wav;base64,${data.audio_data}`);
        audio.play();
    }
}
```

### Python

```python
import requests
import base64
import pygame
import io

def play_audio_from_api():
    response = requests.post(
        "http://localhost:5000/api/tts/base64",
        json={
            "text": "Hello, this is a test of the text to speech API.",
            "voice": "Asteria"
        }
    )
    
    data = response.json()
    
    if data["success"]:
        # Decode base64 audio data
        audio_data = base64.b64decode(data["audio_data"])
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Create a sound object from the audio data
        sound = pygame.mixer.Sound(io.BytesIO(audio_data))
        
        # Play the sound
        sound.play()
        
        # Wait for the sound to finish playing
        pygame.time.wait(int(sound.get_length() * 1000))
```

## Core Components

- `tts_core.py`: Core TTS engine that handles text-to-speech conversion
- `tts_api.py`: Flask API server that exposes the TTS functionality
- `tts_client.py`: Python client library for easy integration
- `tts_cli.py`: Command-line interface for quick text-to-speech conversion
- `templates/index.html`: Web interface for the TTS platform

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Deepgram](https://deepgram.com/) for providing the TTS API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [pygame](https://www.pygame.org/) for audio playback
- [aiohttp](https://docs.aiohttp.org/) for asynchronous HTTP requests
