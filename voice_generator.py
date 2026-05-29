from app_config import secret_value
from elevenlabs.client import ElevenLabs


def text_to_speech_bytes(text):
    """
    Takes text, sends it to ElevenLabs, and returns raw MP3 bytes 
    so Streamlit can play it directly in the browser.
    """
    api_key = secret_value("ELEVENLABS_API_KEY")
    if not api_key:
        print("Voice Generation Error: ELEVENLABS_API_KEY is not configured.")
        return None

    try:
        client = ElevenLabs(api_key=api_key)
        # We use .convert instead of .stream here
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id="pNInz6obpgDQGcFmaJgB", 
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Combine the chunks into a single byte object
        audio_bytes = b"".join([chunk for chunk in audio_generator])
        return audio_bytes

    except Exception as e:
        print(f"Voice Generation Error: {str(e)}")
        return None

# --- Quick Test ---
if __name__ == "__main__":
    test_text = "Hello! I am your autonomous AI development assistant. Everything seems to be wired up perfectly."
    text_to_speech_bytes(test_text)
