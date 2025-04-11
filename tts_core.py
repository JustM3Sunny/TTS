import asyncio
import aiohttp
import base64
import os
import logging
import sys
from typing import Optional, Dict, List

# Try to import pygame, but don't fail if it's not available
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger = logging.getLogger("tts_core")
    logger.warning("pygame is not available. Audio playback will be disabled.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tts_core")

# Available voice models
VOICE_MODELS = {
    "Asteria": "aura-asteria-en",
    "Orpheus": "aura-orpheus-en",
    "Angus": "aura-angus-en",
    "Arcas": "aura-arcas-en",
    "Athena": "aura-athena-en",
    "Helios": "aura-helios-en",
    "Hera": "aura-hera-en",
    "Luna": "aura-luna-en",
    "Orion": "aura-orion-en",
    "Perseus": "aura-perseus-en",
    "Stella": "aura-stella-en",
    "Zeus": "aura-zeus-en"
}

class TTSEngine:
    """Core Text-to-Speech engine using Deepgram API"""

    def __init__(self, default_voice: str = "Asteria", temp_dir: str = "./temp"):
        """
        Initialize the TTS Engine

        Args:
            default_voice: Default voice to use (must be a key in VOICE_MODELS)
            temp_dir: Directory to store temporary audio files
        """
        self.default_voice = default_voice
        self.temp_dir = temp_dir

        # Create temp directory if it doesn't exist
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
        else:
            logger.warning("Audio playback is disabled because pygame is not available.")

    def get_available_voices(self) -> Dict[str, str]:
        """Return a dictionary of available voices"""
        return VOICE_MODELS

    async def generate_audio(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        """
        Generate audio from text using Deepgram API

        Args:
            text: The text to convert to speech
            voice: The voice to use (must be a key in VOICE_MODELS)

        Returns:
            Audio data as bytes or None if generation failed
        """
        if not text:
            logger.error("Empty text provided")
            return None

        # Use default voice if none specified
        selected_voice = voice or self.default_voice

        # Get the model ID for the selected voice
        if selected_voice not in VOICE_MODELS:
            logger.warning(f"Voice '{selected_voice}' not found, using default '{self.default_voice}'")
            model = VOICE_MODELS[self.default_voice]
        else:
            model = VOICE_MODELS[selected_voice]

        url = "https://deepgram.com/api/ttsAudioGeneration"
        payload = {"text": text, "model": model}

        logger.info(f"Generating audio for text: '{text[:50]}...' using voice: {selected_voice}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed with status {response.status}: {error_text}")
                        return None

                    result = await response.json()
                    if 'data' not in result:
                        logger.error(f"Unexpected API response: {result}")
                        return None

                    audio_data = result['data']
                    return base64.b64decode(audio_data)

        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
        except ConnectionResetError as e:
            logger.error(f"Connection reset error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during audio generation: {e}")

        return None

    async def speak_text(self, text: str, voice: Optional[str] = None) -> bool:
        """
        Generate and play audio for the given text

        Args:
            text: The text to speak
            voice: The voice to use

        Returns:
            True if successful, False otherwise
        """
        audio_data = await self.generate_audio(text, voice)
        if not audio_data:
            return False

        return await self.play_audio(audio_data)

    async def play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio data using pygame if available

        Args:
            audio_data: Audio data as bytes

        Returns:
            True if successful, False otherwise
        """
        if not PYGAME_AVAILABLE:
            logger.warning("Cannot play audio: pygame is not available")
            return False

        temp_file = os.path.join(self.temp_dir, f"temp_audio_{id(audio_data)}.wav")

        try:
            with open(temp_file, "wb") as f:
                f.write(audio_data)

            sound = pygame.mixer.Sound(temp_file)
            sound.play()

            # Wait for the audio to finish playing
            while pygame.mixer.get_busy():
                await asyncio.sleep(0.1)

            return True

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_file}: {e}")

    async def save_audio_file(self, text: str, output_path: str, voice: Optional[str] = None) -> bool:
        """
        Generate audio and save it to a file

        Args:
            text: The text to convert to speech
            output_path: Path to save the audio file
            voice: The voice to use

        Returns:
            True if successful, False otherwise
        """
        audio_data = await self.generate_audio(text, voice)
        if not audio_data:
            return False

        try:
            with open(output_path, "wb") as f:
                f.write(audio_data)
            logger.info(f"Audio saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            return False

    def cleanup(self):
        """Clean up resources"""
        if PYGAME_AVAILABLE:
            pygame.mixer.quit()


# Simple test function
async def test_tts_engine():
    engine = TTSEngine()

    print("Available voices:")
    for name, model in engine.get_available_voices().items():
        print(f"- {name} ({model})")

    text = "Hello! This is a test of the text-to-speech engine."
    voice = "Asteria"

    print(f"\nTesting voice: {voice}")
    success = await engine.speak_text(text, voice)

    if success:
        print("Audio played successfully!")
    else:
        print("Failed to generate or play audio.")

    engine.cleanup()


if __name__ == "__main__":
    asyncio.run(test_tts_engine())
