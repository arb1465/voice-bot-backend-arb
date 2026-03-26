from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)
logger.debug('backend/models/record_model.py loaded')


@dataclass
class ConversationRecord:
    """Data model for conversation records"""
    
    user_message: str
    bot_response: str
    timestamp: datetime
    audio_file: str
    response_audio: str
    s3_url: Optional[str] = None
    conversation_id: Optional[str] = None
    duration: Optional[float] = None
    language: str = 'en'
    
    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'timestamp': self.timestamp,
            'audio_file': self.audio_file,
            'response_audio': self.response_audio,
            's3_url': self.s3_url,
            'duration': self.duration,
            'language': self.language
        }
    
    @staticmethod
    def from_dict(data):
        """Create instance from dictionary"""
        return ConversationRecord(
            user_message=data.get('user_message'),
            bot_response=data.get('bot_response'),
            timestamp=data.get('timestamp', datetime.utcnow()),
            audio_file=data.get('audio_file'),
            response_audio=data.get('response_audio'),
            s3_url=data.get('s3_url'),
            conversation_id=str(data.get('_id')) if '_id' in data else None,
            duration=data.get('duration'),
            language=data.get('language', 'en')
        )
