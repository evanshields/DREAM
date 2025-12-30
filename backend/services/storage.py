"""
DREAM AI - File Storage Service
Task 1.11: File Storage Service
PRD Reference: Section 13.1

Supports S3-compatible storage providers:
- AWS S3
- DigitalOcean Spaces
- Supabase Storage
- Local filesystem (development)
"""

import os
import logging
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from botocore.config import Config
from typing import Optional, BinaryIO, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Storage provider types
STORAGE_PROVIDER_S3 = "S3"
STORAGE_PROVIDER_SUPABASE = "SUPABASE"
STORAGE_PROVIDER_GCS = "GCS"
STORAGE_PROVIDER_LOCAL = "LOCAL"

# Default pre-signed URL expiry (15 minutes per PRD Section 13.1)
DEFAULT_PRESIGNED_URL_EXPIRY = 900  # 15 minutes in seconds

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

# ============================================================================
# STORAGE SERVICE CLASS
# ============================================================================

class StorageService:
    """
    Unified storage service for S3-compatible storage providers.
    
    Supports:
    - AWS S3
    - DigitalOcean Spaces (S3-compatible)
    - Supabase Storage (S3-compatible)
    - Local filesystem (development)
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        local_storage_path: Optional[str] = None
    ):
        """
        Initialize storage service.
        
        Args:
            provider: Storage provider (S3, SUPABASE, GCS, LOCAL)
            bucket_name: Bucket name for S3-compatible storage
            region: AWS region or DigitalOcean region
            access_key_id: AWS access key or DigitalOcean Spaces key
            secret_access_key: AWS secret key or DigitalOcean Spaces secret
            endpoint_url: Custom endpoint URL (for DigitalOcean Spaces, Supabase)
            local_storage_path: Local filesystem path (for LOCAL provider)
        """
        # Get configuration from environment variables if not provided
        self.provider = provider or os.getenv("STORAGE_PROVIDER", STORAGE_PROVIDER_S3).upper()
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "dream-ai-documents")
        self.region = region or os.getenv("S3_REGION", "us-east-1")
        self.access_key_id = access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key = secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT_URL")
        self.local_storage_path = local_storage_path or os.getenv("LOCAL_STORAGE_PATH", "./storage")
        
        # Initialize S3 client if not using local storage
        self.s3_client = None
        if self.provider != STORAGE_PROVIDER_LOCAL:
            self._init_s3_client()
        else:
            # Create local storage directory if it doesn't exist
            Path(self.local_storage_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Using local storage at: {self.local_storage_path}")
    
    def _init_s3_client(self):
        """Initialize boto3 S3 client based on provider."""
        try:
            # Configure boto3 with retries
            config = Config(
                retries={
                    'max_attempts': MAX_RETRIES,
                    'mode': 'standard'
                },
                signature_version='s3v4'
            )
            
            # Create S3 client
            client_kwargs = {
                'config': config,
                'region_name': self.region,
            }
            
            # Add credentials if provided
            if self.access_key_id and self.secret_access_key:
                client_kwargs['aws_access_key_id'] = self.access_key_id
                client_kwargs['aws_secret_access_key'] = self.secret_access_key
            
            # Add custom endpoint for DigitalOcean Spaces or Supabase
            if self.endpoint_url:
                client_kwargs['endpoint_url'] = self.endpoint_url
            
            self.s3_client = boto3.client('s3', **client_kwargs)
            
            logger.info(f"Initialized {self.provider} storage client for bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}", exc_info=True)
            raise
    
    def upload(
        self,
        file_content: bytes,
        storage_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload file to storage.
        
        Args:
            file_content: File content as bytes
            storage_path: Path where file should be stored (e.g., "documents/deal_123/file.pdf")
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
        
        Returns:
            Storage path where file was saved
        
        Raises:
            Exception: If upload fails
        """
        try:
            if self.provider == STORAGE_PROVIDER_LOCAL:
                return self._upload_local(file_content, storage_path)
            else:
                return self._upload_s3(file_content, storage_path, content_type, metadata)
                
        except Exception as e:
            logger.error(f"Failed to upload file to {storage_path}: {str(e)}", exc_info=True)
            raise
    
    def _upload_s3(
        self,
        file_content: bytes,
        storage_path: str,
        content_type: Optional[str],
        metadata: Optional[dict]
    ) -> str:
        """Upload file to S3-compatible storage."""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = {str(k): str(v) for k, v in metadata.items()}
            
            # Upload file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                Body=file_content,
                **extra_args
            )
            
            logger.info(f"Successfully uploaded file to S3: {storage_path} ({len(file_content)} bytes)")
            return storage_path
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 upload error ({error_code}): {str(e)}")
            raise Exception(f"Failed to upload file to S3: {error_code}")
        except BotoCoreError as e:
            logger.error(f"Boto3 error during upload: {str(e)}")
            raise Exception(f"Storage service error: {str(e)}")
    
    def _upload_local(
        self,
        file_content: bytes,
        storage_path: str
    ) -> str:
        """Upload file to local filesystem."""
        try:
            # Create full path
            full_path = Path(self.local_storage_path) / storage_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Successfully uploaded file locally: {full_path} ({len(file_content)} bytes)")
            return storage_path
            
        except Exception as e:
            logger.error(f"Local upload error: {str(e)}")
            raise Exception(f"Failed to upload file locally: {str(e)}")
    
    def download(self, storage_path: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            storage_path: Path to file in storage
        
        Returns:
            File content as bytes
        
        Raises:
            Exception: If download fails
        """
        try:
            if self.provider == STORAGE_PROVIDER_LOCAL:
                return self._download_local(storage_path)
            else:
                return self._download_s3(storage_path)
                
        except Exception as e:
            logger.error(f"Failed to download file from {storage_path}: {str(e)}", exc_info=True)
            raise
    
    def _download_s3(self, storage_path: str) -> bytes:
        """Download file from S3-compatible storage."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            
            file_content = response['Body'].read()
            logger.info(f"Successfully downloaded file from S3: {storage_path} ({len(file_content)} bytes)")
            return file_content
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'NoSuchKey':
                raise Exception(f"File not found: {storage_path}")
            logger.error(f"S3 download error ({error_code}): {str(e)}")
            raise Exception(f"Failed to download file from S3: {error_code}")
        except BotoCoreError as e:
            logger.error(f"Boto3 error during download: {str(e)}")
            raise Exception(f"Storage service error: {str(e)}")
    
    def _download_local(self, storage_path: str) -> bytes:
        """Download file from local filesystem."""
        try:
            full_path = Path(self.local_storage_path) / storage_path
            
            if not full_path.exists():
                raise Exception(f"File not found: {storage_path}")
            
            with open(full_path, 'rb') as f:
                file_content = f.read()
            
            logger.info(f"Successfully downloaded file locally: {full_path} ({len(file_content)} bytes)")
            return file_content
            
        except FileNotFoundError:
            raise Exception(f"File not found: {storage_path}")
        except Exception as e:
            logger.error(f"Local download error: {str(e)}")
            raise Exception(f"Failed to download file locally: {str(e)}")
    
    def delete(self, storage_path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            storage_path: Path to file in storage
        
        Returns:
            True if deletion successful
        
        Raises:
            Exception: If deletion fails
        """
        try:
            if self.provider == STORAGE_PROVIDER_LOCAL:
                return self._delete_local(storage_path)
            else:
                return self._delete_s3(storage_path)
                
        except Exception as e:
            logger.error(f"Failed to delete file {storage_path}: {str(e)}", exc_info=True)
            raise
    
    def _delete_s3(self, storage_path: str) -> bool:
        """Delete file from S3-compatible storage."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            
            logger.info(f"Successfully deleted file from S3: {storage_path}")
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 delete error ({error_code}): {str(e)}")
            raise Exception(f"Failed to delete file from S3: {error_code}")
        except BotoCoreError as e:
            logger.error(f"Boto3 error during delete: {str(e)}")
            raise Exception(f"Storage service error: {str(e)}")
    
    def _delete_local(self, storage_path: str) -> bool:
        """Delete file from local filesystem."""
        try:
            full_path = Path(self.local_storage_path) / storage_path
            
            if not full_path.exists():
                logger.warning(f"File not found for deletion: {storage_path}")
                return False
            
            full_path.unlink()
            logger.info(f"Successfully deleted file locally: {full_path}")
            return True
            
        except Exception as e:
            logger.error(f"Local delete error: {str(e)}")
            raise Exception(f"Failed to delete file locally: {str(e)}")
    
    def generate_presigned_url(
        self,
        storage_path: str,
        expiry_seconds: int = DEFAULT_PRESIGNED_URL_EXPIRY,
        http_method: str = "GET"
    ) -> str:
        """
        Generate pre-signed URL for document access.
        
        Per PRD Section 13.1: Pre-signed URLs have 15-minute expiry.
        
        Args:
            storage_path: Path to file in storage
            expiry_seconds: URL expiry time in seconds (default: 900 = 15 minutes)
            http_method: HTTP method (GET for download, PUT for upload)
        
        Returns:
            Pre-signed URL string
        
        Raises:
            Exception: If URL generation fails
        """
        try:
            if self.provider == STORAGE_PROVIDER_LOCAL:
                # For local storage, return a file:// URL or relative path
                # In production, this should be handled differently
                full_path = Path(self.local_storage_path) / storage_path
                return f"file://{full_path.absolute()}"
            
            # Generate pre-signed URL for S3-compatible storage
            url = self.s3_client.generate_presigned_url(
                'get_object' if http_method == "GET" else 'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': storage_path
                },
                ExpiresIn=expiry_seconds
            )
            
            logger.info(f"Generated pre-signed URL for {storage_path} (expires in {expiry_seconds}s)")
            return url
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 presigned URL error ({error_code}): {str(e)}")
            raise Exception(f"Failed to generate pre-signed URL: {error_code}")
        except BotoCoreError as e:
            logger.error(f"Boto3 error generating presigned URL: {str(e)}")
            raise Exception(f"Storage service error: {str(e)}")
    
    def file_exists(self, storage_path: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            storage_path: Path to file in storage
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            if self.provider == STORAGE_PROVIDER_LOCAL:
                full_path = Path(self.local_storage_path) / storage_path
                return full_path.exists()
            else:
                try:
                    self.s3_client.head_object(
                        Bucket=self.bucket_name,
                        Key=storage_path
                    )
                    return True
                except ClientError as e:
                    if e.response.get('Error', {}).get('Code') == '404':
                        return False
                    raise
        except Exception as e:
            logger.error(f"Error checking file existence: {str(e)}")
            return False

# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Global storage service instance (initialized on first use)
_storage_service_instance: Optional[StorageService] = None

def get_storage_service() -> StorageService:
    """
    Get or create storage service instance (singleton pattern).
    
    Returns:
        StorageService instance
    """
    global _storage_service_instance
    
    if _storage_service_instance is None:
        _storage_service_instance = StorageService()
    
    return _storage_service_instance

