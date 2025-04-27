import asyncio
import aiohttp
import base64
import os
import logging
import sys
from typing import Optional, Dict
import tempfile
import hashlib
import shutil
import contextlib

# Try to import pygame, but don't fail if it's not available
try:
    import pygame
    pygame.mixer.pre_init(44100, -16, 2, 2048)  # Initialize mixer early
    pygame.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
except pygame.error as e:
    PYGAME_AVAILABLE = False
    print(f"Pygame initialization error: {e}")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("tts_core")
if not PYGAME_AVAILABLE:
    logger.warning("pygame is not available. Audio playback will be disabled.")


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

    DEEPGRAM_API_URL = "https://api.deepgram.com/v1/speak"  # Updated API endpoint
    TEMP_FILE_PREFIX = "temp_audio_"
    TEMP_FILE_SUFFIX = ".wav"

    def __init__(self, deepgram_api_key: str, default_voice: str = "Asteria", temp_dir: Optional[str] = None):
        """
        Initialize the TTS Engine

        Args:
            deepgram_api_key: The Deepgram API key.
            default_voice: Default voice to use (must be a key in VOICE_MODELS)
            temp_dir: Directory to store temporary audio files. If None, uses system temp dir.
        """
        if not deepgram_api_key:
            raise ValueError("Deepgram API key is required.")

        if default_voice not in VOICE_MODELS:
            raise ValueError(f"Invalid default_voice: {default_voice}. Must be one of {list(VOICE_MODELS.keys())}")

        self.deepgram_api_key = deepgram_api_key
        self.default_voice = default_voice
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="tts_engine_")

        os.makedirs(self.temp_dir, exist_ok=True)  # Ensure temp_dir exists

        # Initialize pygame mixer if available
        self.pygame_initialized = False
        if PYGAME_AVAILABLE:
            try:
                # pygame.mixer.init()  # Already initialized during import
                self.pygame_initialized = True
            except pygame.error as e:
                logger.error(f"Failed to initialize pygame mixer: {e}")
                PYGAME_AVAILABLE = False # Disable pygame if initialization fails
                self.pygame_initialized = False
        else:
            logger.warning("Audio playback is disabled because pygame is not available.")

        self.http_session = None  # Initialize http_session

    async def _get_http_session(self) -> aiohttp.ClientSession:
        """
        Get or create an aiohttp ClientSession.
        """
        if self.http_session is None or self.http_session.closed:
            self.http_session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.deepgram_api_key}",
                         "Content-Type": "application/json"}  # Explicit content type
            )
        return self.http_session

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
            logger.warning("Empty text provided")
            return None

        selected_voice = voice or self.default_voice

        if selected_voice not in VOICE_MODELS:
            logger.warning(f"Voice '{selected_voice}' not found, using default '{self.default_voice}'")
            model = VOICE_MODELS[self.default_voice]
        else:
            model = VOICE_MODELS[selected_voice]

        payload = {"text": text, "voice": model}  # Correct payload format for Deepgram Speak API

        logger.info(f"Generating audio for text: '{text[:50]}...' using voice: {selected_voice}")

        try:
            session = await self._get_http_session()  # Get the session
            async with session.post(self.DEEPGRAM_API_URL, json=payload) as response:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                audio_data = await response.read()  # Get raw audio data directly
                return audio_data

        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error during audio generation: {e}")

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

    @contextlib.asynccontextmanager
    async def _audio_file(self, audio_data: bytes):
        """
        Context manager for creating and cleaning up temporary audio files.
        """
        audio_hash = hashlib.md5(audio_data).hexdigest()
        temp_file = os.path.join(self.temp_dir, f"{self.TEMP_FILE_PREFIX}{audio_hash}{self.TEMP_FILE_SUFFIX}")

        try:
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            yield temp_file
        finally:
            # Ensure cleanup even if there's an exception in the 'with' block
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as e:
                    logger.warning(f"Failed to remove temporary file {temp_file}: {e}")


    async def play_audio(self, audio_data: bytes) -> bool:
        """
        Play audio data using pygame if available

        Args:
            audio_data: Audio data as bytes

        Returns:
            True if successful, False otherwise
        """
        if not PYGAME_AVAILABLE or not self.pygame_initialized:
            logger.warning("Cannot play audio: pygame is not available or initialized")
            return False

        try:
            async with self._audio_file(audio_data) as temp_file:
                try:
                    sound = pygame.mixer.Sound(temp_file)
                    sound.play()

                    # Wait for the audio to finish playing
                    while pygame.mixer.get_busy():
                        await asyncio.sleep(0.1)
                    return True
                except pygame.error as e:
                    logger.error(f"Pygame error playing audio: {e}")
                    return False


        except Exception as e:
            logger.exception(f"Error playing audio: {e}")
            return False


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
            logger.exception(f"Error saving audio file: {e}")
            return False

    async def close(self):
        """Close the aiohttp session."""
        if self.http_session:
            await self.http_session.close()

    def cleanup(self):
        """Clean up resources"""
        if PYGAME_AVAILABLE and self.pygame_initialized:
            pygame.mixer.quit()
        # Clean up the temporary directory
        try:
            shutil.rmtree(self.temp_dir)
            logger.info(f"Temporary directory {self.temp_dir} removed.")
        except OSError as e:
            logger.warning(f"Failed to remove temporary directory {self.temp_dir}: {e}")


# Simple test function
async def test_tts_engine():
    # Replace with your actual Deepgram API key
    deepgram_api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not deepgram_api_key:
        print("Please set the DEEPGRAM_API_KEY environment variable.")
        return

    engine = TTSEngine(deepgram_api_key=deepgram_api_key)

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

    await engine.close()  # Close the aiohttp session
    engine.cleanup()


if __name__ == "__main__":
    asyncio.run(test_tts_engine())