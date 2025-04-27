#!/usr/bin/env python3
import argparse
import asyncio
import os
import sys
import logging
from tts_core import TTSEngine, VOICE_MODELS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def get_text_from_file(file_path: str) -> str | None:
    """
    Reads text from a file. Handles potential errors gracefully.

    Args:
        file_path: The path to the text file.

    Returns:
        The text content of the file, or None if an error occurred.
    """
    try:
        async with asyncio.to_thread(open, file_path, 'r', encoding='utf-8') as f:
            return await asyncio.to_thread(f.read)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except OSError as e:
        logging.error(f"Error reading file: {e}")
        return None


async def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech Command Line Interface")

    # Add arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", "-t", type=str, help="Text to convert to speech")
    group.add_argument("--file", "-f", type=str, help="Text file to convert to speech")
    parser.add_argument("--voice", "-v", type=str, default="Asteria",
                        help=f"Voice to use (default: Asteria). Available voices: {', '.join(VOICE_MODELS.keys())}")
    parser.add_argument("--output", "-o", type=str, help="Output file path (if not specified, audio will be played)")
    parser.add_argument("--list-voices", "-l", action="store_true", help="List available voices")

    args = parser.parse_args()

    # Create TTS engine
    engine = TTSEngine()

    try:
        # List voices
        if args.list_voices:
            print("Available voices:")
            for name, model in engine.get_available_voices().items():
                print(f"- {name} ({model})")
            return

        # Get text from file or command line
        text = None
        if args.text:
            text = args.text
        elif args.file:
            text = await get_text_from_file(args.file)

        if not text:
            logging.error("No text provided. Please use --text or --file.")
            return

        # Check if voice is valid
        if args.voice not in VOICE_MODELS:
            logging.error(f"Error: Voice '{args.voice}' not found. Available voices: {', '.join(VOICE_MODELS.keys())}")
            return

        # Convert text to speech
        try:
            if args.output:
                # Save to file
                logging.info(f"Converting text to speech using voice '{args.voice}' and saving to '{args.output}'...")
                success = await engine.save_audio_file(text, args.output, args.voice)

                if success:
                    logging.info(f"Audio saved to {args.output}")
                else:
                    logging.error("Failed to generate or save audio.")

            else:
                # Play audio
                logging.info(f"Converting text to speech using voice '{args.voice}' and playing audio...")
                success = await engine.speak_text(text, args.voice)

                if not success:
                    logging.error("Failed to generate or play audio.")
        except Exception as e:
            logging.exception("An unexpected error occurred during audio processing:")

    finally:
        # Clean up resources
        try:
            await engine.cleanup()  # Await the cleanup, assuming it's async
        except Exception as e:
            logging.exception(f"Error during cleanup: {e}")


if __name__ == "__main__":
    asyncio.run(main())