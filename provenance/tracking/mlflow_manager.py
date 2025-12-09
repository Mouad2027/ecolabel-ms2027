"""
MLflow Manager for Experiment Tracking
MLflow integration for model experiments and metrics
"""

import os
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import mlflow
try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not installed, using mock mode")


class MLflowManager:
    """Manager for MLflow experiment tracking"""
    
    def __init__(self, tracking_uri: Optional[str] = None):
        """
        Initialize MLflow Manager
        
        Args:
            tracking_uri: MLflow tracking server URI
        """
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI",
            "http://localhost:5000"
        )
        self.mock_experiments: Dict[str, Dict] = {}
        self.mock_runs: Dict[str, Dict] = {}
        
        if MLFLOW_AVAILABLE:
            try:
                mlflow.set_tracking_uri(self.tracking_uri)
                self.client = MlflowClient()
                self.available = True
            except Exception as e:
                logger.warning(f"MLflow connection failed: {e}")
                self.available = False
        else:
            self.available = False
    
    def create_experiment(
        self,
        name: str,
        description: Optional[str] = None,
        parameters: Optional[Dict] = None,
        metrics: Optional[Dict] = None,
        tags: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create MLflow experiment and start a run
        
        Args:
            name: Experiment name
            description: Experiment description
            parameters: Run parameters
            metrics: Initial metrics
            tags: Experiment tags
            
        Returns:
            Dict with experiment info
        """
        experiment_id = str(uuid.uuid4())[:8]
        run_id = str(uuid.uuid4())[:8]
        
        if not self.available:
            # Mock mode
            self.mock_experiments[experiment_id] = {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat()
            }
            self.mock_runs[run_id] = {
                "experiment_id": experiment_id,
                "parameters": parameters or {},
                "metrics": metrics or {},
                "tags": tags or {},
                "status": "running"
            }
            
            return {
                "experiment_id": experiment_id,
                "name": name,
                "run_id": run_id,
                "status": "mock",
                "artifact_uri": f"mock://artifacts/{experiment_id}/{run_id}"
            }
        
        try:
            # Create or get experiment
            experiment = mlflow.get_experiment_by_name(name)
            if experiment is None:
                exp_id = mlflow.create_experiment(
                    name,
                    tags={"description": description or ""}
                )
            else:
                exp_id = experiment.experiment_id
            
            # Start run
            with mlflow.start_run(experiment_id=exp_id) as run:
                # Log parameters
                if parameters:
                    for key, value in parameters.items():
                        mlflow.log_param(key, value)
                
                # Log metrics
                if metrics:
                    for key, value in metrics.items():
                        mlflow.log_metric(key, value)
                
                # Set tags
                if tags:
                    for key, value in tags.items():
                        mlflow.set_tag(key, value)
                
                return {
                    "experiment_id": exp_id,
                    "name": name,
                    "run_id": run.info.run_id,
                    "status": "created",
                    "artifact_uri": run.info.artifact_uri
                }
        except Exception as e:
            logger.error(f"MLflow experiment creation error: {e}")
            return {
                "experiment_id": experiment_id,
                "name": name,
                "run_id": None,
                "status": "error",
                "error": str(e)
            }
    
    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get experiment details
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Experiment details or None
        """
        if not self.available:
            exp = self.mock_experiments.get(experiment_id)
            if exp:
                return {
                    "experiment_id": experiment_id,
                    **exp,
                    "status": "mock"
                }
            return None
        
        try:
            experiment = self.client.get_experiment(experiment_id)
            return {
                "experiment_id": experiment.experiment_id,
                "name": experiment.name,
                "artifact_location": experiment.artifact_location,
                "lifecycle_stage": experiment.lifecycle_stage,
                "tags": dict(experiment.tags)
            }
        except Exception as e:
            logger.error(f"Get experiment error: {e}")
            return None
    
    def list_experiments(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List all experiments
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of experiments
        """
        if not self.available:
            return [
                {"experiment_id": k, **v, "status": "mock"}
                for k, v in list(self.mock_experiments.items())[:limit]
            ]
        
        try:
            experiments = self.client.search_experiments(max_results=limit)
            return [
                {
                    "experiment_id": exp.experiment_id,
                    "name": exp.name,
                    "artifact_location": exp.artifact_location,
                    "lifecycle_stage": exp.lifecycle_stage
                }
                for exp in experiments
            ]
        except Exception as e:
            logger.error(f"List experiments error: {e}")
            return []
    
    def log_metrics(
        self,
        run_id: str,
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Log metrics to a run
        
        Args:
            run_id: Run ID
            metrics: Metrics to log
            
        Returns:
            Status dict
        """
        if not self.available:
            if run_id in self.mock_runs:
                self.mock_runs[run_id]["metrics"].update(metrics)
            return {"status": "mock", "logged": metrics}
        
        try:
            with mlflow.start_run(run_id=run_id):
                for key, value in metrics.items():
                    mlflow.log_metric(key, value)
            return {"status": "logged", "metrics": metrics}
        except Exception as e:
            logger.error(f"Log metrics error: {e}")
            return {"status": "error", "error": str(e)}
    
    def log_artifact(
        self,
        run_id: str,
        local_path: str,
        artifact_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log artifact to a run
        
        Args:
            run_id: Run ID
            local_path: Path to artifact
            artifact_path: Path in artifact store
            
        Returns:
            Status dict
        """
        if not self.available:
            return {
                "status": "mock",
                "artifact": local_path,
                "run_id": run_id
            }
        
        try:
            with mlflow.start_run(run_id=run_id):
                mlflow.log_artifact(local_path, artifact_path)
            return {
                "status": "logged",
                "artifact": local_path,
                "run_id": run_id
            }
        except Exception as e:
            logger.error(f"Log artifact error: {e}")
            return {"status": "error", "error": str(e)}
    
    def end_run(self, run_id: str, status: str = "FINISHED") -> Dict[str, Any]:
        """
        End a run
        
        Args:
            run_id: Run ID
            status: Final status
            
        Returns:
            Status dict
        """
        if not self.available:
            if run_id in self.mock_runs:
                self.mock_runs[run_id]["status"] = status.lower()
            return {"status": "mock", "run_status": status}
        
        try:
            self.client.set_terminated(run_id, status)
            return {"status": "ended", "run_status": status}
        except Exception as e:
            logger.error(f"End run error: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get run details
        
        Args:
            run_id: Run ID
            
        Returns:
            Run details or None
        """
        if not self.available:
            run = self.mock_runs.get(run_id)
            if run:
                return {"run_id": run_id, **run}
            return None
        
        try:
            run = self.client.get_run(run_id)
            return {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "artifact_uri": run.info.artifact_uri,
                "params": dict(run.data.params),
                "metrics": dict(run.data.metrics),
                "tags": dict(run.data.tags)
            }
        except Exception as e:
            logger.error(f"Get run error: {e}")
            return None
