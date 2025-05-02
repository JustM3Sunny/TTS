import aiohttp
import asyncio
import base64
import os
import logging
from typing import Optional, Dict, List, Union, BinaryIO, Tuple, Any
from aiohttp import ClientSession, ClientResponse, ContentTypeError, ClientError
import functools
import json

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
        self._closed = False  # Flag to indicate if the client has been closed

    async def _get_session(self) -> ClientSession:
        """
        Get or create an aiohttp ClientSession.
        """
        async with self._session_lock:
            if self._closed:
                raise RuntimeError("Client is closed and cannot create a new session.")
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession()  # Explicitly use aiohttp
            return self._session

    async def close(self):
        """Close the aiohttp ClientSession."""
        async with self._session_lock:
            if self._session:
                await self._session.close()
            self._session = None  # Ensure the session is set to None after closing
            self._closed = True

    async def _safe_api_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Tuple[Optional[Union[Dict[str, Any], bytes, str]], Optional[int]]:
        """
        Handles API requests with centralized error handling and response parsing.
        """
        url = f"{self.api_url}{endpoint}"
        try:
            session = await self._get_session()
            async with session.request(method, url, json=data) as response:
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    try:
                        return await response.json(), response.status
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode JSON from URL: {url}")
                        return None, response.status
                elif 'audio/' in content_type:
                    return await response.read(), response.status
                else:
                    return await response.text(), response.status

        except aiohttp.ClientResponseError as e:
            logger.error(f"API request failed: {e.status} - {e.message} for URL: {url}")
            return None, e.status
        except aiohttp.ContentTypeError as e:
            logger.error(f"Invalid content type received from URL: {url}. Error: {e}")
            return None, None
        except aiohttp.ClientError as e:
            logger.error(f"Client error: {e} for URL: {url}")
            return None, None
        except Exception as e:
            logger.exception(f"Unexpected error during API request to URL: {url}")
            return None, None

    async def get_available_voices(self) -> Dict[str, str]:
        """
        Get a list of available voices from the API

        Returns:
            Dictionary of voice names and their model IDs
        """
        response, status = await self._safe_api_request("GET", "/api/voices")
        if response and isinstance(response, dict) and response.get("success", False) and "voices" in response:
            return response["voices"]
        else:
            logger.warning(f"Invalid response from API: {response}, Status: {status}")
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

        response, status = await self._safe_api_request("POST", "/api/tts", data=payload)
        if isinstance(response, bytes):
            return response
        else:
            logger.warning(f"TTS conversion failed. Response: {response}, Status: {status}")
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

        response, status = await self._safe_api_request("POST", "/api/tts/base64", data=payload)

        if response and isinstance(response, dict) and response.get("success", False) and "audio_data" in response:
            return response["audio_data"]
        else:
            logger.warning(f"Base64 TTS conversion failed. Response: {response}, Status: {status}")
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

            # Use a dedicated thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_audio_file, output_path, audio_data)

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