import os
import logging
from gtts import gTTS
from datetime import datetime

logger = logging.getLogger(__name__)

logger.debug('backend/services/tts_service.py loaded')


def text_to_speech(text, language='en', output_path=None):
    """
    Convert text to speech using Google Text-to-Speech
    
    Args:
        text (str): Text to convert to speech
        language (str): Language code (default: 'en')
        output_path (str): Optional output file path
        
    Returns:
        str: Path to generated audio file
    """
    try:
        logger.debug('text_to_speech called', extra={'text_preview': text[:80] if text else None})
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f'tmp/response_{timestamp}.mp3'
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # Generate speech
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(output_path)
        
        logger.info(f"TTS audio saved: {output_path}")
        logger.debug('text_to_speech: saved output', extra={'output_path': output_path})
        return output_path
        
    except Exception as e:
        logger.error(f"Error converting text to speech: {str(e)}")
        return None


def text_to_speech_stream(text, language='en'):
    """
    Convert text to speech and return audio stream
    Useful for real-time playback
    
    Args:
        text (str): Text to convert
        language (str): Language code
        
    Returns:
        bytes: Audio stream data
    """
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        # Save to BytesIO instead of file
        from io import BytesIO
        audio_stream = BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        return audio_stream.getvalue()
        
    except Exception as e:
        logger.error(f"Error streaming TTS: {str(e)}")
        return None


def text_to_speech_advanced(text, language='en', speed=1.0, output_path=None):
    """
    Convert text to speech with advanced options
    
    Args:
        text (str): Text to convert
        language (str): Language code
        speed (float): Speech speed (not all providers support this)
        output_path (str): Output file path
        
    Returns:
        str: Path to audio file
    """
    # Note: gTTS doesn't support speed adjustment natively
    # For speed control, consider using Google Cloud TTS API
    return text_to_speech(text, language, output_path)
