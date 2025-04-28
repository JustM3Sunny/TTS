import aiohttp
import asyncio
import base64
import os
import logging
from typing import Optional, Dict, List, Union, BinaryIO, Tuple
from aiohttp import ClientSession, ClientResponse, ContentTypeError, ClientError
import functools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tts_client")


class TTSClient:
    """Client for the Text-to-Speech API"""

    def __init__(self, api_url: str = "http://localhost:5000"):
        """
        Initialize the TTS Client

        Args:
            api_url: URL of the TTS API server
        """
        self.api_url = api_url
        self._session: Optional[ClientSession] = None
        self._session_lock = asyncio.Lock()  # Add a lock for session creation

    async def _get_session(self) -> ClientSession:
        """
        Get or create an aiohttp ClientSession.
        """
        async with self._session_lock:
            if self._session is None or self._session.closed:
                self._session = ClientSession()
            return self._session

    async def close(self):
        """Close the aiohttp ClientSession."""
        if self._session:
            await self._session.close()
            self._session = None  # Ensure the session is set to None after closing

    async def get_available_voices(self) -> Dict[str, str]:
        """
        Get a list of available voices from the API

        Returns:
            Dictionary of voice names and their model IDs
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.api_url}/api/voices") as response:
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                data = await response.json()
                if data.get("success", False) and "voices" in data:
                    return data["voices"]
                else:
                    logger.warning(f"Invalid response from API: {data}")  # Use warning
                    return {}
        except aiohttp.ClientResponseError as e:
            logger.error(f"API request failed: {e.status} - {e.message}")
            return {}
        except ContentTypeError:
            logger.error("Invalid JSON response received")
            return {}
        except ClientError as e:
            logger.error(f"Client error: {e}")
            return {}
        except Exception as e:
            logger.exception("Unexpected error getting voices")  # Log full traceback
            return {}

    async def text_to_speech(self, text: str, voice: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech using the API

        Args:
            text: The text to convert to speech
            voice: The voice to use (optional)

        Returns:
            Audio data as bytes or None if conversion failed
        """
        if not text:
            logger.warning("Empty text provided")  # Use warning instead of error
            return None

        payload = {"text": text}
        if voice:
            payload["voice"] = voice

        try:
            session = await self._get_session()
            async with session.post(f"{self.api_url}/api/tts", json=payload) as response:
                response.raise_for_status()
                return await response.read()
        except aiohttp.ClientResponseError as e:
            logger.error(f"API request failed: {e.status} - {e.message}")
            return None
        except ClientError as e:
            logger.error(f"Client error: {e}")
            return None
        except Exception as e:
            logger.exception("Unexpected error in text_to_speech")
            return None

    async def text_to_speech_base64(self, text: str, voice: Optional[str] = None) -> Optional[str]:
        """
        Convert text to speech and get base64 encoded audio

        Args:
            text: The text to convert to speech
            voice: The voice to use (optional)

        Returns:
            Base64 encoded audio data or None if conversion failed
        """
        if not text:
            logger.warning("Empty text provided")  # Use warning instead of error
            return None

        payload = {"text": text}
        if voice:
            payload["voice"] = voice

        try:
            session = await self._get_session()
            async with session.post(f"{self.api_url}/api/tts/base64", json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("success", False) and "audio_data" in data:
                    return data["audio_data"]
                else:
                    logger.warning(f"Invalid response from API: {data}")  # Use warning
                    return None
        except aiohttp.ClientResponseError as e:
            logger.error(f"API request failed: {e.status} - {e.message}")
            return None
        except ContentTypeError:
            logger.error("Invalid JSON response received")
            return None
        except ClientError as e:
            logger.error(f"Client error: {e}")
            return None
        except Exception as e:
            logger.exception("Unexpected error in text_to_speech_base64")
            return None

    async def save_audio_file(self, text: str, output_path: str, voice: Optional[str] = None) -> bool:
        """
        Convert text to speech and save to a file

        Args:
            text: The text to convert to speech
            output_path: Path to save the audio file
            voice: The voice to use (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            audio_data = await self.text_to_speech(text, voice)
            if not audio_data:
                return False

            # Use functools.partial to pass arguments to _write_audio_file
            await asyncio.get_event_loop().run_in_executor(
                None, functools.partial(self._write_audio_file, output_path, audio_data)
            )

            logger.info(f"Audio saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            return False

    def _write_audio_file(self, output_path: str, audio_data: bytes):
        """Writes the audio data to a file in a blocking manner."""
        try:
            with open(output_path, "wb") as f:
                f.write(audio_data)
        except Exception as e:
            logger.error(f"Error writing to file {output_path}: {e}")


# Example usage
async def example_usage():
    client = TTSClient()

    try:
        # Get available voices
        voices = await client.get_available_voices()
        print("Available voices:")
        if voices:
            for name, model in voices.items():
                print(f"- {name} ({model})")
        else:
            print("No voices available.")

        # Convert text to speech and save to file
        text = "Hello! This is a test of the text-to-speech client library."
        voice = "Asteria"

        print(f"\nConverting text to speech using voice: {voice}")
        success = await client.save_audio_file(text, "example_output.wav", voice)

        if success:
            print(f"Audio saved to example_output.wav")
        else:
            print("Failed to generate or save audio.")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(example_usage())