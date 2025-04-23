#!/usr/bin/env python3
import argparse
import asyncio
import os
import sys
import logging
from tts_core import TTSEngine, VOICE_MODELS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    text = f.read()
            except FileNotFoundError:
                logging.error(f"File not found: {args.file}")
                return
            except Exception as e:
                logging.error(f"Error reading file: {e}")
                return

        # Check if voice is valid
        if args.voice not in VOICE_MODELS:
            logging.error(f"Error: Voice '{args.voice}' not found. Available voices: {', '.join(VOICE_MODELS.keys())}")
            return

        # Convert text to speech
        if args.output:
            # Save to file
            logging.info(f"Converting text to speech using voice '{args.voice}' and saving to '{args.output}'...")
            try:
                success = await engine.save_audio_file(text, args.output, args.voice)

                if success:
                    logging.info(f"Audio saved to {args.output}")
                else:
                    logging.error("Failed to generate or save audio.")
            except Exception as e:
                logging.exception("An unexpected error occurred during audio saving:")

        else:
            # Play audio
            logging.info(f"Converting text to speech using voice '{args.voice}' and playing audio...")
            try:
                success = await engine.speak_text(text, args.voice)

                if not success:
                    logging.error("Failed to generate or play audio.")
            except Exception as e:
                logging.exception("An unexpected error occurred during audio playback:")

    finally:
        # Clean up resources
        await engine.cleanup()  # Await the cleanup, assuming it's async

if __name__ == "__main__":
    asyncio.run(main())