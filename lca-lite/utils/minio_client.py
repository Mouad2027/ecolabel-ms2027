"""
MinIO Storage Client
Stores LCA calculation artifacts and results
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False


class MinioStorage:
    """
    MinIO client for storing LCA artifacts
    """
    
    BUCKET_NAME = "lca-calculations"
    PROVENANCE_BUCKET = "provenance-logs"
    
    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        secure: bool = False
    ):
        """
        Initialize MinIO client
        
        Args:
            endpoint: MinIO server endpoint
            access_key: Access key
            secret_key: Secret key
            secure: Use HTTPS
        """
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.secure = secure
        
        self.client = None
        self._initialized = False
        
    def _ensure_initialized(self):
        """Lazy initialization of MinIO client"""
        if self._initialized:
            return
        
        if not MINIO_AVAILABLE:
            return
        
        try:
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            # Create buckets if they don't exist
            self._ensure_bucket(self.BUCKET_NAME)
            self._ensure_bucket(self.PROVENANCE_BUCKET)
            
            self._initialized = True
        except Exception as e:
            # TODO: Add proper logging
            self._initialized = False
    
    def _ensure_bucket(self, bucket_name: str):
        """Create bucket if it doesn't exist"""
        if not self.client:
            return
        
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
        except S3Error:
            pass
    
    def store_calculation(
        self,
        calculation_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Store LCA calculation data
        
        Args:
            calculation_id: Unique calculation ID
            data: Calculation data to store
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_initialized()
        
        if not self.client:
            return False
        
        try:
            # Add metadata
            data["stored_at"] = datetime.utcnow().isoformat()
            
            # Convert to JSON bytes
            json_data = json.dumps(data, indent=2, default=str)
            data_bytes = json_data.encode('utf-8')
            
            # Create object name with date path
            date_path = datetime.utcnow().strftime("%Y/%m/%d")
            object_name = f"{date_path}/{calculation_id}.json"
            
            # Upload to MinIO
            from io import BytesIO
            self.client.put_object(
                self.BUCKET_NAME,
                object_name,
                BytesIO(data_bytes),
                len(data_bytes),
                content_type="application/json"
            )
            
            return True
            
        except Exception as e:
            # TODO: Add proper logging
            return False
    
    def get_calculation(self, calculation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve LCA calculation data
        
        Args:
            calculation_id: Calculation ID
            
        Returns:
            Calculation data or None
        """
        self._ensure_initialized()
        
        if not self.client:
            return None
        
        try:
            # Search for the object (simplified - in production use metadata index)
            objects = self.client.list_objects(
                self.BUCKET_NAME,
                recursive=True
            )
            
            for obj in objects:
                if calculation_id in obj.object_name:
                    response = self.client.get_object(
                        self.BUCKET_NAME,
                        obj.object_name
                    )
                    data = json.loads(response.read().decode('utf-8'))
                    response.close()
                    response.release_conn()
                    return data
            
            return None
            
        except Exception:
            return None
    
    def store_provenance(
        self,
        score_id: str,
        provenance_data: Dict[str, Any]
    ) -> bool:
        """
        Store provenance/lineage data
        
        Args:
            score_id: Score ID
            provenance_data: Provenance information
            
        Returns:
            True if successful
        """
        self._ensure_initialized()
        
        if not self.client:
            return False
        
        try:
            provenance_data["stored_at"] = datetime.utcnow().isoformat()
            
            json_data = json.dumps(provenance_data, indent=2, default=str)
            data_bytes = json_data.encode('utf-8')
            
            date_path = datetime.utcnow().strftime("%Y/%m/%d")
            object_name = f"{date_path}/provenance_{score_id}.json"
            
            from io import BytesIO
            self.client.put_object(
                self.PROVENANCE_BUCKET,
                object_name,
                BytesIO(data_bytes),
                len(data_bytes),
                content_type="application/json"
            )
            
            return True
            
        except Exception:
            return False
    
    def list_calculations(
        self,
        prefix: str = None,
        limit: int = 100
    ) -> list:
        """
        List stored calculations
        
        Args:
            prefix: Optional prefix filter (e.g., date path)
            limit: Maximum number of results
            
        Returns:
            List of calculation object names
        """
        self._ensure_initialized()
        
        if not self.client:
            return []
        
        try:
            objects = self.client.list_objects(
                self.BUCKET_NAME,
                prefix=prefix,
                recursive=True
            )
            
            results = []
            for obj in objects:
                if len(results) >= limit:
                    break
                results.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None
                })
            
            return results
            
        except Exception:
            return []
    
    def delete_calculation(self, object_name: str) -> bool:
        """
        Delete a calculation object
        
        Args:
            object_name: Full object name/path
            
        Returns:
            True if successful
        """
        self._ensure_initialized()
        
        if not self.client:
            return False
        
        try:
            self.client.remove_object(self.BUCKET_NAME, object_name)
            return True
        except Exception:
            return False
