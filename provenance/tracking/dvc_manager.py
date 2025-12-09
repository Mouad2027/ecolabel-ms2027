"""
DVC Manager for Dataset Versioning
Data Version Control integration for tracking datasets
"""

import os
import hashlib
import subprocess
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DVCManager:
    """Manager for DVC dataset versioning"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize DVC Manager
        
        Args:
            repo_path: Path to DVC repository (default: current directory)
        """
        self.repo_path = repo_path or os.getcwd()
        self.dvc_initialized = self._check_dvc_init()
    
    def _check_dvc_init(self) -> bool:
        """Check if DVC is initialized in repo"""
        dvc_dir = Path(self.repo_path) / ".dvc"
        return dvc_dir.exists()
    
    def init(self) -> Dict[str, Any]:
        """Initialize DVC in repository"""
        try:
            result = subprocess.run(
                ["dvc", "init"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            self.dvc_initialized = True
            return {
                "status": "initialized",
                "output": result.stdout
            }
        except FileNotFoundError:
            logger.warning("DVC not installed, using mock mode")
            return {"status": "mock", "message": "DVC not installed"}
        except Exception as e:
            logger.error(f"DVC init error: {e}")
            return {"status": "error", "message": str(e)}
    
    def track_file(self, file_path: str) -> Dict[str, Any]:
        """
        Track a file with DVC
        
        Args:
            file_path: Path to file to track
            
        Returns:
            Dict with tracking result
        """
        # Compute file hash
        file_hash = self._compute_file_hash(file_path)
        
        if not self.dvc_initialized:
            # Mock mode if DVC not available
            logger.info(f"Mock tracking file: {file_path}")
            return {
                "status": "mock",
                "hash": file_hash,
                "file_path": file_path,
                "dvc_file": f"{file_path}.dvc"
            }
        
        try:
            result = subprocess.run(
                ["dvc", "add", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            dvc_file = f"{file_path}.dvc"
            
            return {
                "status": "tracked",
                "hash": file_hash,
                "file_path": file_path,
                "dvc_file": dvc_file,
                "output": result.stdout
            }
        except Exception as e:
            logger.error(f"DVC track error: {e}")
            return {
                "status": "error",
                "hash": file_hash,
                "message": str(e)
            }
    
    def checkout_version(
        self,
        dvc_file: str,
        commit_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Checkout specific version of tracked file
        
        Args:
            dvc_file: Path to .dvc file
            commit_hash: Git commit hash for specific version
            
        Returns:
            Dict with checkout result
        """
        if not self.dvc_initialized:
            return {"status": "mock", "message": "Mock checkout"}
        
        try:
            if commit_hash:
                # Checkout specific git commit first
                subprocess.run(
                    ["git", "checkout", commit_hash, "--", dvc_file],
                    cwd=self.repo_path,
                    capture_output=True
                )
            
            # DVC checkout
            result = subprocess.run(
                ["dvc", "checkout", dvc_file],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "checked_out",
                "dvc_file": dvc_file,
                "output": result.stdout
            }
        except Exception as e:
            logger.error(f"DVC checkout error: {e}")
            return {"status": "error", "message": str(e)}
    
    def push(self, remote: str = "origin") -> Dict[str, Any]:
        """
        Push tracked files to remote storage
        
        Args:
            remote: DVC remote name
            
        Returns:
            Dict with push result
        """
        if not self.dvc_initialized:
            return {"status": "mock", "message": "Mock push"}
        
        try:
            result = subprocess.run(
                ["dvc", "push", "-r", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "pushed",
                "remote": remote,
                "output": result.stdout
            }
        except Exception as e:
            logger.error(f"DVC push error: {e}")
            return {"status": "error", "message": str(e)}
    
    def pull(self, remote: str = "origin") -> Dict[str, Any]:
        """
        Pull tracked files from remote storage
        
        Args:
            remote: DVC remote name
            
        Returns:
            Dict with pull result
        """
        if not self.dvc_initialized:
            return {"status": "mock", "message": "Mock pull"}
        
        try:
            result = subprocess.run(
                ["dvc", "pull", "-r", remote],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "pulled",
                "remote": remote,
                "output": result.stdout
            }
        except Exception as e:
            logger.error(f"DVC pull error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of file"""
        try:
            path = Path(file_path)
            if not path.exists():
                return hashlib.sha256(file_path.encode()).hexdigest()
            
            sha256 = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return hashlib.sha256(file_path.encode()).hexdigest()
    
    def get_status(self) -> Dict[str, Any]:
        """Get DVC status"""
        if not self.dvc_initialized:
            return {"status": "not_initialized"}
        
        try:
            result = subprocess.run(
                ["dvc", "status"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "ok",
                "output": result.stdout
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
