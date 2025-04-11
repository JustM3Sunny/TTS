#!/usr/bin/env python3
import argparse
import asyncio
import os
import sys
from tts_core import TTSEngine, VOICE_MODELS

async def main():
    parser = argparse.ArgumentParser(description="Text-to-Speech Command Line Interface")
    
    # Add arguments
    parser.add_argument("--text", "-t", type=str, help="Text to convert to speech")
    parser.add_argument("--file", "-f", type=str, help="Text file to convert to speech")
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
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        else:
            parser.print_help()
            return
            
        # Check if voice is valid
        if args.voice not in VOICE_MODELS:
            print(f"Error: Voice '{args.voice}' not found. Available voices: {', '.join(VOICE_MODELS.keys())}")
            return
            
        # Convert text to speech
        if args.output:
            # Save to file
            print(f"Converting text to speech using voice '{args.voice}'...")
            success = await engine.save_audio_file(text, args.output, args.voice)
            
            if success:
                print(f"Audio saved to {args.output}")
            else:
                print("Failed to generate or save audio.")
        else:
            # Play audio
            print(f"Converting text to speech using voice '{args.voice}'...")
            print("Playing audio...")
            success = await engine.speak_text(text, args.voice)
            
            if not success:
                print("Failed to generate or play audio.")
    finally:
        # Clean up resources
        engine.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
