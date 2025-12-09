"""
Cloudinary Service
Handles file uploads to Cloudinary
"""
from typing import Optional, Dict, Any
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# Make cloudinary import optional
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    logger.warning("cloudinary package not installed. File upload features will be disabled.")
    cloudinary = None
    cloudinary_uploader = None
    cloudinary_api = None
    CLOUDINARY_AVAILABLE = False

class CloudinaryService:
    def __init__(self):
        """Initialize Cloudinary with credentials"""
        if not CLOUDINARY_AVAILABLE:
            logger.warning("cloudinary package not available. File upload features will be disabled.")
            self.enabled = False
            return
            
        if not all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
            logger.warning("Cloudinary credentials not configured. File uploads will be disabled.")
            self.enabled = False
            return
        
        try:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True
            )
            self.enabled = True
            logger.info("Cloudinary service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudinary service: {e}")
            self.enabled = False
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = 'knowledge-base',
        resource_type: str = 'auto'
    ) -> Optional[Dict[str, Any]]:
        """
        Upload file to Cloudinary
        
        Args:
            file_content: File content as bytes
            file_name: Original file name
            folder: Cloudinary folder path
            resource_type: Resource type (auto, image, raw, video)
        
        Returns:
            Dict with public_id, url, secure_url, format, etc. or None if failed
        """
        if not self.enabled:
            logger.warning("Cloudinary not enabled, cannot upload file")
            return None
        
        if not CLOUDINARY_AVAILABLE:
            logger.warning("cloudinary package not available, cannot upload file")
            return None
            
        try:
            # Generate unique public_id from file_name
            public_id = f"{folder}/{file_name.rsplit('.', 1)[0]}"
            
            result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                folder=folder,
                resource_type=resource_type,
                overwrite=False,
                unique_filename=True
            )
            
            logger.info(f"File uploaded successfully: {result.get('public_id')}")
            return {
                "public_id": result.get('public_id'),
                "url": result.get('url'),
                "secure_url": result.get('secure_url'),
                "format": result.get('format'),
                "width": result.get('width'),
                "height": result.get('height'),
                "bytes": result.get('bytes'),
                "created_at": result.get('created_at')
            }
        except Exception as e:
            logger.error(f"Error uploading file to Cloudinary: {e}")
            return None
    
    def delete_file(self, public_id: str) -> bool:
        """Delete file from Cloudinary"""
        if not self.enabled or not CLOUDINARY_AVAILABLE:
            logger.warning("Cloudinary not enabled or not available, cannot delete file")
            return False
        
        try:
            result = cloudinary.uploader.destroy(public_id)
            if result.get('result') == 'ok':
                logger.info(f"File deleted successfully: {public_id}")
                return True
            else:
                logger.warning(f"File deletion returned: {result.get('result')}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file from Cloudinary: {e}")
            return False
    
    def get_file_url(self, public_id: str, transformation: Optional[Dict] = None) -> Optional[str]:
        """Get optimized URL for a file"""
        if not self.enabled or not CLOUDINARY_AVAILABLE:
            return None
        
        try:
            if transformation:
                url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
            else:
                url = cloudinary.CloudinaryImage(public_id).build_url()
            return url
        except Exception as e:
            logger.error(f"Error generating file URL: {e}")
            return None

# Singleton instance
cloudinary_service = CloudinaryService()

