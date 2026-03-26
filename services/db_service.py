import os
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

logger = logging.getLogger(__name__)

logger.debug('backend/services/db_service.py loaded')

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('MONGODB_DB_NAME', 'voice_bot')

# Initialize MongoDB client
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME] if client else None


def get_db():
    """Get database connection"""
    logger.debug('get_db called')
    return db


def save_conversation(conversation_data):
    """
    Save conversation to MongoDB
    
    Args:
        conversation_data (dict): Conversation data to save
        
    Returns:
        ObjectId: ID of inserted document or None
    """
    try:
        preview = (conversation_data.get('user_message') or "")[:80]

        logger.debug(
            'save_conversation called',
            extra={'user_message_preview': preview}
        )

        if db is None:
            logger.warning("MongoDB not configured, conversation not saved")
            return None

        collection = db['conversations']
        result = collection.insert_one(conversation_data)
        logger.info(f"Conversation saved with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")
        return None


def get_conversations(limit=50):
    """
    Get all conversations
    
    Args:
        limit (int): Maximum number of conversations to retrieve
        
    Returns:
        list: List of conversation documents
    """
    try:
        if db is None:
            logger.warning("MongoDB not configured")
            return []
        
        collection = db['conversations']
        conversations = list(collection.find().sort('_id', -1).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
        
        return conversations
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}")
        return []


def get_conversation_by_id(conversation_id):
    """
    Get specific conversation by ID
    
    Args:
        conversation_id (str): Conversation ID
        
    Returns:
        dict: Conversation document or None
    """
    try:
        if db is None:
            logger.warning("MongoDB not configured")
            return None
        
        collection = db['conversations']
        conversation = collection.find_one({'_id': ObjectId(conversation_id)})
        
        if conversation:
            conversation['_id'] = str(conversation['_id'])
        
        return conversation
        
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}")
        return None


def update_conversation(conversation_id, update_data):
    """
    Update conversation
    
    Args:
        conversation_id (str): Conversation ID
        update_data (dict): Data to update
        
    Returns:
        bool: True if successful
    """
    try:
        if db is None:
            logger.warning("MongoDB not configured")
            return False
        
        collection = db['conversations']
        result = collection.update_one(
            {'_id': ObjectId(conversation_id)},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        logger.error(f"Error updating conversation: {str(e)}")
        return False


def delete_conversation(conversation_id):
    """
    Delete conversation
    
    Args:
        conversation_id (str): Conversation ID
        
    Returns:
        bool: True if successful
    """
    try:
        if db is None:
            logger.warning("MongoDB not configured")
            return False
        
        collection = db['conversations']
        result = collection.delete_one({'_id': ObjectId(conversation_id)})
        
        return result.deleted_count > 0
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return False


def delete_all_conversations():
    """
    Delete all conversations (use with caution)
    
    Returns:
        int: Number of documents deleted
    """
    try:
        if db is None:
            logger.warning("MongoDB not configured")
            return 0
        
        collection = db['conversations']
        result = collection.delete_many({})
        logger.info(f"Deleted {result.deleted_count} conversations")
        
        return result.deleted_count
        
    except Exception as e:
        logger.error(f"Error deleting conversations: {str(e)}")
        return 0


def search_conversations(query, field='user_message'):
    """
    Search conversations by text
    
    Args:
        query (str): Search query
        field (str): Field to search in
        
    Returns:
        list: Matching conversations
    """
    try:
        if db is None:
            logger.warning("MongoDB not configured")
            return []
        
        collection = db['conversations']
        conversations = list(collection.find(
            {field: {'$regex': query, '$options': 'i'}}
        ).sort('_id', -1))
        
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
        
        return conversations
        
    except Exception as e:
        logger.error(f"Error searching conversations: {str(e)}")
        return []


def get_conversation_stats():
    """
    Get conversation statistics
    
    Returns:
        dict: Statistics about conversations
    """
    try:
        if db is None:
            logger.warning("MongoDB not configured")
            return {}
        
        collection = db['conversations']
        total = collection.count_documents({})
        
        return {
            'total_conversations': total,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {}
