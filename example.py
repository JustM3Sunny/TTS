#!/usr/bin/env python3
import asyncio
import os
from tts_core import TTSEngine

async def demo_all_voices():
    """Demonstrate all available voices"""
    engine = TTSEngine()
    
    # Create output directory if it doesn't exist
    os.makedirs("voice_samples", exist_ok=True)
    
    # Get all available voices
    voices = engine.get_available_voices()
    
    # Sample text to convert to speech
    text = "Hello! This is a demonstration of the text-to-speech platform with different voices."
    
    print("Generating audio samples for all voices...")
    
    # Generate audio for each voice
    for voice_name in voices.keys():
        print(f"Processing voice: {voice_name}")
        
        # Generate and save audio file
        output_path = f"voice_samples/{voice_name.lower()}_sample.wav"
        success = await engine.save_audio_file(text, output_path, voice_name)
        
        if success:
            print(f"  ✓ Audio saved to {output_path}")
        else:
            print(f"  ✗ Failed to generate audio for {voice_name}")
    
    print("\nAll voice samples generated!")
    print("You can find the audio samples in the 'voice_samples' directory.")
    
    # Clean up resources
    engine.cleanup()

async def interactive_demo():
    """Interactive demonstration of the TTS engine"""
    engine = TTSEngine()
    
    print("=== Interactive Text-to-Speech Demo ===")
    print("Available voices:")
    
    # Get all available voices
    voices = engine.get_available_voices()
    for i, name in enumerate(voices.keys(), 1):
        print(f"{i}. {name}")
    
    # Get user input
    while True:
        try:
            voice_index = int(input("\nSelect a voice (number): ")) - 1
            if voice_index < 0 or voice_index >= len(voices):
                print("Invalid selection. Please try again.")
                continue
            break
        except ValueError:
            print("Please enter a number.")
    
    voice_name = list(voices.keys())[voice_index]
    print(f"Selected voice: {voice_name}")
    
    # Get text to convert to speech
    text = input("\nEnter text to convert to speech: ")
    
    print(f"\nConverting text to speech using voice '{voice_name}'...")
    print("Playing audio...")
    
    # Generate and play audio
    success = await engine.speak_text(text, voice_name)
    
    if not success:
        print("Failed to generate or play audio.")
    
    # Ask if user wants to save the audio
    save_audio = input("\nDo you want to save this audio? (y/n): ").lower()
    if save_audio == 'y':
        output_path = input("Enter output file path (default: output.wav): ") or "output.wav"
        
        # Generate and save audio file
        success = await engine.save_audio_file(text, output_path, voice_name)
        
        if success:
            print(f"Audio saved to {output_path}")
        else:
            print("Failed to save audio.")
    
    # Clean up resources
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
