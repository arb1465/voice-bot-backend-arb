# services/stt_service.py

import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

logger.debug('backend/services/stt_service.py loaded')

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(file_path: str):
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )

        return transcript.text

    except Exception as e:
        print("Error transcribing audio:", e)
        return None

def get_audio_duration(audio_file_path):
    """
    Get duration of audio file in seconds
    
    Args:
        audio_file_path (str): Path to audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        import librosa
        y, sr = librosa.load(audio_file_path)
        duration = librosa.get_duration(y=y, sr=sr)
        return duration
    except Exception as e:
        logger.error(f"Error getting audio duration: {str(e)}")
        return None
