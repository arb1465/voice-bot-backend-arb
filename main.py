import sys
sys.stdout.reconfigure(encoding='utf-8')
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
# Load environment variables as early as possible so service modules can access them
load_dotenv()

from services.stt_service import transcribe_audio
from services.gpt_service import generate_response
from services.tts_service import text_to_speech
from services.storage_service import upload_to_s3
from services.db_service import save_conversation, get_conversations, get_conversation_by_id
from utils.logger import setup_logger


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logger = setup_logger(__name__)

# Debug: main module loaded
logger.info('backend/main.py loaded')

# Create temp directory if not exists
os.makedirs('tmp', exist_ok=True)

@app.route('/')
def home():
    return {
        "message": "Voice Bot Backend is running 🚀",
        "endpoints": [
            "/api/health",
            "/api/upload",
            "/api/conversations"
        ]
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.debug('health_check called')
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


@app.route('/api/upload', methods=['POST'])
def upload_audio():
    """
    Upload and process audio file
    Expected: audio file in request.files['audio']
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Save temporary audio file
        temp_path = f'tmp/{datetime.now().timestamp()}.wav'
        audio_file.save(temp_path)
        logger.info(f"Audio file saved: {temp_path}")
        logger.debug('upload_audio: saved temp file', extra={'temp_path': temp_path})

        # Step 1: Transcribe audio
        logger.debug('upload_audio: starting transcription')
        user_message = transcribe_audio(temp_path)
        logger.info(f"Transcribed: {user_message}")

        if not user_message:
            return jsonify({'error': 'Could not transcribe audio'}), 400

        # Step 2: Generate response
        logger.debug('upload_audio: generating response')
        bot_response = generate_response(user_message)
        logger.info(f"Generated response: {bot_response}")

        # Step 3: Convert to speech
        logger.debug('upload_audio: converting text to speech')
        audio_response_path = text_to_speech(bot_response)
        logger.info(f"Audio response created: {audio_response_path}")

        # Step 4: Upload to S3 (optional)
        logger.debug('upload_audio: uploading response audio to storage')
        s3_url = upload_to_s3(audio_response_path)

        # Step 5: Save conversation to database
        logger.debug('upload_audio: saving conversation to DB')
        conversation = {
            'timestamp': datetime.utcnow(),
            'user_message': user_message,
            'bot_response': bot_response,
            'audio_file': temp_path,
            'response_audio': audio_response_path,
            's3_url': s3_url
        }
        db_id = save_conversation(conversation)
        logger.debug('upload_audio: saved conversation', extra={'db_id': str(db_id)})

        # Cleanup temp files (optional)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        filename = os.path.basename(audio_response_path)
        base_url = request.host_url.rstrip('/')

        return jsonify({
            'success': True,
            'conversation_id': str(db_id),
            'user_message': user_message,
            'bot_response': bot_response,
            'audio_response': f"{base_url}/tmp/{filename}",
            's3_url': s3_url
        }), 200

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversations', methods=['GET'])
def get_all_conversations():
    """Get all conversations"""
    try:
        conversations = get_conversations()
        return jsonify({
            'success': True,
            'count': len(conversations),
            'conversations': conversations
        }), 200
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_single_conversation(conversation_id):
    """Get specific conversation by ID"""
    try:
        conversation = get_conversation_by_id(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404

        return jsonify({
            'success': True,
            'conversation': conversation
        }), 200
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversations', methods=['DELETE'])
def delete_all_conversations():
    """Delete all conversations (for testing)"""
    try:
        from services.db_service import delete_all_conversations as db_delete_all
        db_delete_all()
        return jsonify({'success': True, 'message': 'All conversations deleted'}), 200
    except Exception as e:
        logger.error(f"Error deleting conversations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/tmp/<filename>')
def serve_audio(filename):
    return send_from_directory('tmp', filename)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=int(port), debug=debug)