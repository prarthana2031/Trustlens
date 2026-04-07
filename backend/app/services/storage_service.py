from app.core.config import settings
from supabase import create_client
from typing import Optional
from datetime import datetime
import uuid
import logging
import os
import json
import time

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # Fail fast with a clear message if env isn't loaded.
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise RuntimeError(
                "Supabase config missing. Ensure backend/.env contains SUPABASE_URL and SUPABASE_SERVICE_KEY, then restart the server."
            )

        # Normalize values to avoid hidden CRLF/quotes breaking JWT parsing.
        raw_url = settings.SUPABASE_URL
        raw_key = settings.SUPABASE_SERVICE_KEY
        url = (raw_url or "").strip().strip('"').strip("'")
        key = (raw_key or "").strip().strip('"').strip("'")

        # Safe diagnostics (no secrets)
        raw_key_len = len(raw_key or "")
        key_len = len(key)
        key_tail = (key or "")[-6:]
        logger.warning(
            "StorageService init: bucket=%s supabase_url=%s service_key_len=%s(raw=%s) service_key_tail=%s",
            settings.STORAGE_BUCKET_NAME,
            url,
            key_len,
            raw_key_len,
            key_tail,
        )

        # Use SERVICE_KEY for storage operations to bypass RLS policies
        self.client = create_client(
            url,
            key,
        )
        self.bucket_name = settings.STORAGE_BUCKET_NAME
        
    def ensure_bucket_exists(self):
        """Ensure storage bucket exists"""
        try:
            # Get storage instance correctly
            storage = self.client.storage
            
            # List buckets
            buckets = storage.list_buckets()
            bucket_exists = any(bucket.name == self.bucket_name for bucket in buckets)
            
            if not bucket_exists:
                storage.create_bucket(self.bucket_name, {'public': False})
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket already exists: {self.bucket_name}")
        except Exception as e:
            logger.warning(f"Could not verify bucket: {str(e)}")
    
    def upload_file(self, file_content: bytes, original_filename: str, content_type: str) -> dict:
        """Upload file to Supabase storage"""
        try:
            logger.warning(
                "Storage upload start: bucket=%s filename=%s bytes=%s content_type=%s",
                self.bucket_name,
                original_filename,
                len(file_content) if file_content else 0,
                content_type,
            )
            # Generate unique filename
            file_extension = original_filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
            file_path = unique_filename
            
            # Get storage instance
            storage = self.client.storage
            
            # Upload to bucket with correct content type
            storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                {"content-type": content_type}
            )
            
            # Generate signed URL for private buckets
            signed_url = storage.from_(self.bucket_name).create_signed_url(
                file_path,
                settings.STORAGE_URL_EXPIRY
            )
            file_url = signed_url.get("signedURL")
            
            logger.info(f"File uploaded successfully: {file_path}")
            
            return {
                "file_path": file_path,
                "file_url": file_url,
                "file_name": unique_filename,
                "original_name": original_filename,
                "file_size": len(file_content),
                "file_type": content_type
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise Exception(f"Storage upload failed: {str(e)}")
    
    def get_file_url(self, file_path: str, expires_in: int = None) -> str:
        """Get signed URL for file access"""
        try:
            expiry = expires_in or settings.STORAGE_URL_EXPIRY
            storage = self.client.storage
            
            # Create signed URL
            signed_url = storage.from_(self.bucket_name).create_signed_url(file_path, expiry)
            return signed_url['signedURL']
            
        except Exception as e:
            logger.error(f"Failed to get file URL: {str(e)}")
            raise
    
    def delete_file(self, file_path: str):
        """Delete file from storage"""
        try:
            storage = self.client.storage
            storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"File deleted: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            raise

# Create instance
storage_service = StorageService()