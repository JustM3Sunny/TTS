#!/usr/bin/env python3
import asyncio
import os
import logging
from tts_core import TTSEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def demo_all_voices():
    """Demonstrate all available voices"""
    try:
        engine = TTSEngine()

        # Create output directory if it doesn't exist
        output_dir = "voice_samples"
        os.makedirs(output_dir, exist_ok=True)

        # Get all available voices
        voices = engine.get_available_voices()

        # Sample text to convert to speech
        text = "Hello! This is a demonstration of the text-to-speech platform with different voices."

        logging.info("Generating audio samples for all voices...")

        # Generate audio for each voice
        for voice_name in voices.keys():
            logging.info(f"Processing voice: {voice_name}")

            # Generate and save audio file
            output_path = os.path.join(output_dir, f"{voice_name.lower()}_sample.wav")
            try:
                success = await engine.save_audio_file(text, output_path, voice_name)

                if success:
                    logging.info(f"  ✓ Audio saved to {output_path}")
                else:
                    logging.error(f"  ✗ Failed to generate audio for {voice_name}")
            except Exception as e:
                logging.exception(f"An error occurred while processing voice {voice_name}: {e}")

        logging.info("\nAll voice samples generated!")
        logging.info(f"You can find the audio samples in the '{output_dir}' directory.")

    except Exception as e:
        logging.exception(f"An unexpected error occurred in demo_all_voices: {e}")
    finally:
        if 'engine' in locals():
            engine.cleanup()


async def interactive_demo():
    """Interactive demonstration of the TTS engine"""
    try:
        engine = TTSEngine()

        print("=== Interactive Text-to-Speech Demo ===")
        print("Available voices:")

        # Get all available voices
        voices = engine.get_available_voices()
        voice_list = list(voices.keys())  # Store voices in a list for easier indexing
        for i, name in enumerate(voice_list, 1):
            print(f"{i}. {name}")

        # Get user input
        while True:
            try:
                voice_index = int(input("\nSelect a voice (number): ")) - 1
                if 0 <= voice_index < len(voice_list):
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a number.")

        voice_name = voice_list[voice_index]
        print(f"Selected voice: {voice_name}")

        # Get text to convert to speech
        text = input("\nEnter text to convert to speech: ")

        print(f"\nConverting text to speech using voice '{voice_name}'...")
        print("Playing audio...")

        # Generate and play audio
        try:
            success = await engine.speak_text(text, voice_name)

            if not success:
                print("Failed to generate or play audio.")
        except Exception as e:
            logging.exception(f"An error occurred during audio playback: {e}")

        # Ask if user wants to save the audio
        save_audio = input("\nDo you want to save this audio? (y/n): ").lower()
        if save_audio == 'y':
            output_path = input("Enter output file path (default: output.wav): ") or "output.wav"

            # Generate and save audio file
            try:
                success = await engine.save_audio_file(text, output_path, voice_name)

                if success:
                    print(f"Audio saved to {output_path}")
                else:
                    print("Failed to save audio.")
            except Exception as e:
                logging.exception(f"An error occurred while saving the audio: {e}")

    except Exception as e:
        logging.exception(f"An unexpected error occurred in interactive_demo: {e}")
    finally:
        if 'engine' in locals():
            engine.cleanup()


async def main():
    """Main function"""
    print("=== Text-to-Speech Platform Demo ===")
    print("1. Generate samples for all voices")
    print("2. Interactive demo")

    choice = input("\nSelect an option (1-2): ")

    if choice == "1":
        await demo_all_voices()
    elif choice == "2":
        await interactive_demo()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    asyncio.run(main())