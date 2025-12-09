"""
Provenance Database Models
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from database.connection import Base


class ProvenanceRecordDB(Base):
    """Provenance record for score tracking"""
    __tablename__ = "provenance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    score_id = Column(String(100), unique=True, index=True, nullable=False)
    product_id = Column(String(100), index=True, nullable=False)
    pipeline_version = Column(String(50), nullable=False)
    
    # Data lineage
    data_sources = Column(JSON, nullable=False, default=list)
    transformations = Column(JSON, nullable=False, default=list)
    
    # Model information
    model_info = Column(JSON, nullable=True)
    
    # Metrics
    metrics = Column(JSON, nullable=True)
    
    # Integrity
    data_hash = Column(String(64), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProvenanceRecord(score_id={self.score_id}, pipeline={self.pipeline_version})>"


class DatasetVersionDB(Base):
    """Dataset version tracking"""
    __tablename__ = "dataset_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    version = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    dvc_file = Column(String(500), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    schema_info = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DatasetVersion(name={self.name}, version={self.version})>"


class ExperimentRunDB(Base):
    """MLflow experiment run tracking"""
    __tablename__ = "experiment_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(100), index=True, nullable=False)
    run_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    
    # Parameters and metrics
    parameters = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(50), default="running")
    artifact_uri = Column(String(500), nullable=True)
    
    # Timestamps
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<ExperimentRun(run_id={self.run_id}, status={self.status})>"
