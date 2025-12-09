"""
CRUD Operations for Provenance Service
"""

import hashlib
import json
from sqlalchemy.orm import Session
from typing import Optional, List
from models.provenance import ProvenanceRecordDB, DatasetVersionDB


def compute_data_hash(data: dict) -> str:
    """Compute hash of provenance data for integrity"""
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def get_provenance_by_score_id(
    db: Session,
    score_id: str
) -> Optional[ProvenanceRecordDB]:
    """Get provenance record by score ID"""
    return db.query(ProvenanceRecordDB).filter(
        ProvenanceRecordDB.score_id == score_id
    ).first()


def create_provenance_record(
    db: Session,
    data: dict
) -> ProvenanceRecordDB:
    """Create new provenance record"""
    # Compute data hash for integrity
    data_hash = compute_data_hash({
        "score_id": data["score_id"],
        "product_id": data["product_id"],
        "data_sources": data["data_sources"],
        "transformations": data["transformations"]
    })
    
    record = ProvenanceRecordDB(
        score_id=data["score_id"],
        product_id=data["product_id"],
        pipeline_version=data["pipeline_version"],
        data_sources=data["data_sources"],
        transformations=data["transformations"],
        model_info=data.get("model_info"),
        metrics=data.get("metrics"),
        data_hash=data_hash
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_provenance_records(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[ProvenanceRecordDB]:
    """Get all provenance records with pagination"""
    return db.query(ProvenanceRecordDB).offset(skip).limit(limit).all()


def create_dataset_version(
    db: Session,
    name: str,
    version: str,
    file_path: str,
    file_hash: str,
    dvc_file: Optional[str] = None,
    description: Optional[str] = None,
    schema_info: Optional[dict] = None
) -> DatasetVersionDB:
    """Create dataset version record"""
    record = DatasetVersionDB(
        name=name,
        version=version,
        file_path=file_path,
        file_hash=file_hash,
        dvc_file=dvc_file,
        description=description,
        schema_info=schema_info
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_dataset_versions(
    db: Session,
    name: str
) -> List[DatasetVersionDB]:
    """Get all versions of a dataset"""
    return db.query(DatasetVersionDB).filter(
        DatasetVersionDB.name == name
    ).order_by(DatasetVersionDB.created_at.desc()).all()


def get_dataset_version(
    db: Session,
    name: str,
    version: str
) -> Optional[DatasetVersionDB]:
    """Get specific dataset version"""
    return db.query(DatasetVersionDB).filter(
        DatasetVersionDB.name == name,
        DatasetVersionDB.version == version
    ).first()


def get_latest_dataset_version(
    db: Session,
    name: str
) -> Optional[DatasetVersionDB]:
    """Get latest version of a dataset"""
    return db.query(DatasetVersionDB).filter(
        DatasetVersionDB.name == name
    ).order_by(DatasetVersionDB.created_at.desc()).first()
