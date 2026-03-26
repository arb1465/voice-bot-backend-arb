import os
import logging
from google.cloud import storage
from google.api_core.exceptions import GoogleAPICallError

logger = logging.getLogger(__name__)

logger.debug('backend/services/storage_service.py loaded')

# Initialize GCS client
try:
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        gcs_client = storage.Client()
    else:
        # Use default credentials
        gcs_client = storage.Client()
except Exception as e:
    logger.warning(f"GCS initialization warning: {str(e)}")
    gcs_client = None

BUCKET_NAME = os.getenv('GCP_BUCKET_NAME')
logger.debug('storage_service config', extra={'bucket': BUCKET_NAME})


def upload_to_gcs(file_path, object_name=None):
    """
    Upload a file to Google Cloud Storage bucket
    
    Args:
        file_path (str): Local file path to upload
        object_name (str): GCS object name (if None, uses filename)
        
    Returns:
        str: GCS file URL or None if upload failed
    """
    try:
        if not BUCKET_NAME:
            logger.warning("GCP_BUCKET_NAME not configured, skipping GCS upload")
            return None
        
        if not gcs_client:
            logger.warning("GCS client not initialized")
            return None
        
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        # Get bucket and upload file
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_filename(file_path)
        
        logger.info(f"File uploaded to GCS: gs://{BUCKET_NAME}/{object_name}")
        
        # Generate GCS URL
        gcs_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return gcs_url
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except GoogleAPICallError as e:
        logger.error(f"GCS error uploading file: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error uploading to GCS: {str(e)}")
        return None


# Backward compatibility alias
def upload_to_s3(file_path, object_name=None):
    """Alias for upload_to_gcs for backward compatibility"""
    return upload_to_gcs(file_path, object_name)


def download_from_gcs(object_name, download_path):
    """
    Download a file from Google Cloud Storage bucket
    
    Args:
        object_name (str): GCS object name
        download_path (str): Local path to save file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not BUCKET_NAME:
            logger.warning("GCP_BUCKET_NAME not configured")
            return False
        
        if not gcs_client:
            logger.warning("GCS client not initialized")
            return False
        
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.download_to_filename(download_path)
        logger.info(f"File downloaded from GCS: {download_path}")
        return True
        
    except GoogleAPICallError as e:
        logger.error(f"GCS error downloading file: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error downloading from GCS: {str(e)}")
        return False


# Backward compatibility alias
def download_from_s3(object_name, download_path):
    """Alias for download_from_gcs for backward compatibility"""
    return download_from_gcs(object_name, download_path)


def delete_from_gcs(object_name):
    """
    Delete a file from Google Cloud Storage bucket
    
    Args:
        object_name (str): GCS object name
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not BUCKET_NAME:
            logger.warning("GCP_BUCKET_NAME not configured")
            return False
        
        if not gcs_client:
            logger.warning("GCS client not initialized")
            return False
        
        bucket = gcs_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.delete()
        logger.info(f"File deleted from GCS: {object_name}")
        return True
        
    except GoogleAPICallError as e:
        logger.error(f"GCS error deleting file: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error deleting from GCS: {str(e)}")
        return False


# Backward compatibility alias
def delete_from_s3(object_name):
    """Alias for delete_from_gcs for backward compatibility"""
    return delete_from_gcs(object_name)


def list_gcs_files(prefix=''):
    """
    List files in Google Cloud Storage bucket
    
    Args:
        prefix (str): Prefix to filter files
        
    Returns:
        list: List of file names
    """
    try:
        if not BUCKET_NAME:
            logger.warning("GCP_BUCKET_NAME not configured")
            return []
        
        if not gcs_client:
            logger.warning("GCS client not initialized")
            return []
        
        bucket = gcs_client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs(prefix=prefix)
        files = [blob.name for blob in blobs]
        return files
        
    except Exception as e:
        logger.error(f"Error listing GCS files: {str(e)}")
        return []


# Backward compatibility alias
def list_s3_files(prefix=''):
    """Alias for list_gcs_files for backward compatibility"""
    return list_gcs_files(prefix)
