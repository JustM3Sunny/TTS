#!/usr/bin/env python3
import asyncio
import os
import logging
import signal
from tts_core import TTSEngine  # Assuming this is a custom module
from concurrent.futures import ThreadPoolExecutor
import functools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a global thread pool executor
MAX_WORKERS = os.cpu_count() or 4  # Use CPU count or default to 4
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


async def run_in_executor(func, *args, **kwargs):
    """Helper function to run a function in the thread pool executor."""
    loop = asyncio.get_running_loop()
    bound_func = functools.partial(func, *args, **kwargs)
    try:
        return await loop.run_in_executor(executor, bound_func)
    except asyncio.CancelledError:
        logging.warning("Task cancelled while running in executor.")
        return None
    except Exception as e:
        logging.error(f"Error in run_in_executor: {e}", exc_info=True)
        raise


async def demo_all_voices():
    """Demonstrate all available voices"""
    output_dir = "voice_samples"
    os.makedirs(output_dir, exist_ok=True)

    engine = TTSEngine()  # Initialize engine here
    try:
        voices = engine.get_available_voices()
        text = "Hello! This is a demonstration of the text-to-speech platform with different voices."

        logging.info("Generating audio samples for all voices...")

        async def process_voice(voice_name):
            logging.info(f"Processing voice: {voice_name}")
            output_path = os.path.join(output_dir, f"{voice_name.lower()}_sample.wav")
            try:
                await run_in_executor(engine.save_audio_file, text, output_path, voice_name)
                logging.info(f"  ✓ Audio saved to {output_path}")
            except Exception as e:
                logging.exception(f"An error occurred while processing voice {voice_name}: {e}")

        # Use asyncio.gather to run voice processing concurrently
        await asyncio.gather(*(process_voice(voice_name) for voice_name in voices))

        logging.info("\nAll voice samples generated!")
        logging.info(f"You can find the audio samples in the '{output_dir}' directory.")

    except Exception as e:
        logging.exception(f"An unexpected error occurred in demo_all_voices: {e}")
    finally:
        try:
            engine.cleanup()
        except Exception as e:
            logging.exception(f"Error during engine cleanup: {e}")


async def interactive_demo():
    """Interactive demonstration of the TTS engine"""
    engine = TTSEngine()  # Initialize engine here
    try:
        print("=== Interactive Text-to-Speech Demo ===")
        print("Available voices:")

        voices = engine.get_available_voices()
        voice_list = list(voices.keys())
        for i, name in enumerate(voice_list, 1):
            print(f"{i}. {name}")

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

        text = input("\nEnter text to convert to speech: ")

        print(f"\nConverting text to speech using voice '{voice_name}'...")
        print("Playing audio...")

        try:
            await run_in_executor(engine.speak_text, text, voice_name)
        except Exception as e:
            logging.exception(f"An error occurred during audio playback: {e}")

        save_audio = input("\nDo you want to save this audio? (y/n): ").lower()
        if save_audio == 'y':
            output_path = input("Enter output file path (default: output.wav): ") or "output.wav"

            try:
                await run_in_executor(engine.save_audio_file, text, output_path, voice_name)
                print(f"Audio saved to {output_path}")
            except Exception as e:
                logging.exception(f"An error occurred while saving the audio: {e}")

    except Exception as e:
        logging.exception(f"An unexpected error occurred in interactive_demo: {e}")
    finally:
        try:
            engine.cleanup()
        except Exception as e:
            logging.exception(f"Error during engine cleanup: {e}")


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
    async def shutdown(signal_name):
        """Cancel all tasks and shutdown the event loop."""
        logging.info(f"Received exit signal {signal_name}...")
        logging.info("Shutting down thread pool executor...")
        executor.shutdown(wait=True)
        logging.info("Cancelling all pending tasks...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        logging.info(f"Releasing event loop resources...")
        asyncio.get_event_loop().stop()

    loop = asyncio.get_event_loop()

    # Install signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, functools.partial(asyncio.create_task, shutdown(sig.name)))

    try:
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        logging.info("Main task cancelled.")
    finally:
        logging.info("Closing event loop.")
        loop.close()