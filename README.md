# 🎙️ Advanced Text-to-Speech Platform

<div align="center">

![TTS Platform Banner](https://user-images.githubusercontent.com/74038190/241765453-85cb9521-97c0-4a65-9358-7db8099fac7f.gif)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Site-blue?style=for-the-badge&logo=koyeb)](https://tts-platform-vibee-12020407.koyeb.app)
[![GitHub Stars](https://img.shields.io/github/stars/JustM3Sunny/TTS?style=for-the-badge&logo=github)](https://github.com/JustM3Sunny/TTS/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/JustM3Sunny/TTS?style=for-the-badge&logo=github)](https://github.com/JustM3Sunny/TTS/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/JustM3Sunny/TTS?style=for-the-badge&logo=github)](https://github.com/JustM3Sunny/TTS/issues)
[![License](https://img.shields.io/github/license/JustM3Sunny/TTS?style=for-the-badge)](LICENSE)

</div>

A powerful and flexible text-to-speech platform that converts text to speech with multiple voice options. This platform is designed to be easily integrated into other projects and applications.

## ✨ Features

- 🔊 **12 High-Quality Voices** - Choose from a variety of natural-sounding voices
- 🌐 **Web Interface** - User-friendly interface for easy testing and usage
- 🔌 **REST API** - Simple API for integration with other applications
- 📦 **Multiple Integration Options** - Python, Node.js, and web browser support
- 🚀 **Deployed on Koyeb** - Reliable cloud hosting for 24/7 availability
- 🔄 **Asynchronous Processing** - Fast and responsive text-to-speech conversion

## 🎭 Available Voices

| Voice | Description | Voice ID |
|-------|-------------|----------|
| Asteria | Female, Neutral | aura-asteria-en |
| Orpheus | Male, Neutral | aura-orpheus-en |
| Angus | Male, Scottish | aura-angus-en |
| Arcas | Male, Neutral | aura-arcas-en |
| Athena | Female, Neutral | aura-athena-en |
| Helios | Male, Neutral | aura-helios-en |
| Hera | Female, Neutral | aura-hera-en |
| Luna | Female, Neutral | aura-luna-en |
| Orion | Male, Neutral | aura-orion-en |
| Perseus | Male, Neutral | aura-perseus-en |
| Stella | Female, Neutral | aura-stella-en |
| Zeus | Male, Authoritative | aura-zeus-en |

## 🚀 Live Demo

Try the platform now at: [https://tts-platform-vibee-12020407.koyeb.app](https://tts-platform-vibee-12020407.koyeb.app)

![Demo Screenshot](https://user-images.githubusercontent.com/74038190/216649417-9acc58ff-9910-4f5a-b07b-8d7485645396.png)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for Node.js integration)
- pip (Python package manager)

### Local Setup

1. Clone this repository:
```bash
git clone https://github.com/JustM3Sunny/TTS.git
cd TTS
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python deploy.py
```

4. Open your web browser and navigate to:
```
http://localhost:5000
```

## 🔌 API Usage

### REST API Endpoints

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

### Python Integration

```python
import requests
import base64

def text_to_speech(text, voice="Asteria"):
    response = requests.post(
        "https://tts-platform-vibee-12020407.koyeb.app/api/tts/base64",
        json={
            "text": text,
            "voice": voice
        }
    )

    data = response.json()

    if data["success"]:
        # Decode base64 audio data
        audio_data = base64.b64decode(data["audio_data"])

        # Save to file
        with open("output.wav", "wb") as f:
            f.write(audio_data)

        print("Audio saved to output.wav")
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")

# Example usage
text_to_speech("Hello, this is a test of the text to speech API.", "Zeus")
```

### Node.js Integration with Axios

```javascript
const axios = require('axios');
const fs = require('fs');

async function textToSpeech(text, voice = 'Asteria') {
    try {
        const response = await axios.post(
            'https://tts-platform-vibee-12020407.koyeb.app/api/tts/base64',
            {
                text: text,
                voice: voice
            }
        );

        const data = response.data;

        if (data.success) {
            // Decode base64 audio data
            const buffer = Buffer.from(data.audio_data, 'base64');

            // Save to file
            fs.writeFileSync('output.wav', buffer);

            console.log('Audio saved to output.wav');
        } else {
            console.error(`Error: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Example usage
textToSpeech('Hello, this is a test of the text to speech API.', 'Zeus');
```

### Web Browser Integration

```html
<script>
async function convertTextToSpeech() {
    const text = document.getElementById('textInput').value;
    const voice = document.getElementById('voiceSelect').value;

    const response = await fetch('https://tts-platform-vibee-12020407.koyeb.app/api/tts/base64', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text,
            voice: voice
        })
    });

    const data = await response.json();

    if (data.success) {
        // Create audio from base64 data
        const audio = new Audio(`data:audio/wav;base64,${data.audio_data}`);
        audio.play();
    } else {
        alert(`Error: ${data.error || 'Unknown error'}`);
    }
}
</script>

<textarea id="textInput">Hello, this is a test.</textarea>
<select id="voiceSelect">
    <option value="Asteria">Asteria</option>
    <option value="Zeus">Zeus</option>
    <!-- Add more voices as needed -->
</select>
<button onclick="convertTextToSpeech()">Speak</button>
```

## 📋 Command-Line Interface

The platform includes a command-line interface for quick text-to-speech conversion:

```bash
# List available voices
python tts_cli.py --list-voices

# Convert text to speech and play it
python tts_cli.py --text "Hello, this is a test." --voice "Zeus"

# Convert text from a file to speech and save it to an audio file
python tts_cli.py --file input.txt --voice "Luna" --output output.wav
```

## 🧩 Core Components

- `tts_core.py`: Core TTS engine that handles text-to-speech conversion
- `tts_api.py`: Flask API server that exposes the TTS functionality
- `tts_client.py`: Python client library for easy integration
- `tts_cli.py`: Command-line interface for quick text-to-speech conversion
- `templates/index.html`: Web interface for the TTS platform

## 🔧 Advanced Usage

### Batch Processing

For processing multiple text files:

```python
import os
from tts_client import TTSClient

async def batch_process(input_dir, output_dir, voice="Asteria"):
    client = TTSClient("https://tts-platform-vibee-12020407.koyeb.app")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process each text file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace(".txt", ".wav"))

            # Read text from file
            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Convert text to speech and save to file
            await client.save_audio_file(text, output_path, voice)
            print(f"Processed {filename} -> {os.path.basename(output_path)}")
```

### Custom Integration

The platform is designed to be easily integrated into other applications. You can use the API directly or use the provided client libraries.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

If you have any questions or suggestions, please open an issue on GitHub.

---

<div align="center">

Made with ❤️ by [JustM3Sunny](https://github.com/JustM3Sunny)

</div>