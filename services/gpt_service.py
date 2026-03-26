import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

logger.debug('backend/services/gpt_service.py loaded')

# System message for the bot
SYSTEM_MESSAGE = """You are a helpful and friendly voice assistant. 
You provide concise, clear responses suitable for text-to-speech conversion.
Keep your responses under 200 words to ensure good user experience.
Be conversational.
Language rules:
- Default: English
- If user explicitly speaks Hindi → reply in Hindi
- Gujarati → only if explicitly requested
- Otherwise NEVER switch language
"""


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(user_message: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Error generating response:", e)
        return "Sorry, I am not able to response. Please try again."

def generate_response_with_context(user_message):
    """
    Generate response with full conversation context
    
    Args:
        user_message (str): Current user message
        conversation_history (list): List of {role, content} dicts
        
    Returns:
        str: Generated response
    """
    return generate_response(user_message)
