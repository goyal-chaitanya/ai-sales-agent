# audio_processor.py

import os
from openai import OpenAI

from app_config import secret_value

# --- OPTION A: If you want to use OpenAI (Requires paid credits) ---
# client = OpenAI() 
# WHISPER_MODEL = "whisper-1"

# --- OPTION B: If you want to use Groq (Free Tier) ---
# Groq hosts an incredibly fast version of Whisper completely free
WHISPER_MODEL = "whisper-large-v3" 


def transcribe_audio(file_path):
    """
    Takes a path to an audio file (.wav, .mp3, etc.), 
    sends it to the Whisper API, and returns the transcript string.
    """
    if not os.path.exists(file_path):
        return f"Error: The file {file_path} does not exist."

    api_key = secret_value("GROQ_API_KEY")
    if not api_key:
        return "Transcription Error: GROQ_API_KEY is not configured."

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        # Open the audio file in 'rb' (read-binary) mode
        with open(file_path, "rb") as audio_file:
            print(f"Transcribing {file_path} using Whisper...")
            
            # Modern OpenAI/Groq SDK call structure
            transcription = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file
            )
            
            # Return the raw text string from the response
            return transcription.text

    except Exception as e:
        return f"Transcription Error: {str(e)}"


# --- Quick Test ---
if __name__ == "__main__":
    # To test this, drop a small sample .wav or .mp3 file into your folder 
    # and rename it to 'test.wav'
    test_file = "test.mp3" 
    
    result = transcribe_audio(test_file)
    print("\n--- TRANSCRIPTION RESULT ---")
    print(result)
