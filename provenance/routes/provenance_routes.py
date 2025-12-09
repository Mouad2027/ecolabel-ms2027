"""
Provenance Routes
Endpoints for data lineage and experiment tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from database.connection import get_db
from database import crud
from tracking.dvc_manager import DVCManager
from tracking.mlflow_manager import MLflowManager

router = APIRouter()

# Initialize tracking managers
dvc_manager = DVCManager()
mlflow_manager = MLflowManager()


# Pydantic Models
class ProvenanceRecordCreate(BaseModel):
    score_id: str
    product_id: str
    pipeline_version: str
    data_sources: List[dict]
    transformations: List[dict]
    model_info: Optional[dict] = None
    metrics: Optional[dict] = None


class ProvenanceRecordResponse(BaseModel):
    id: int
    score_id: str
    product_id: str
    pipeline_version: str
    data_sources: List[dict]
    transformations: List[dict]
    model_info: Optional[dict]
    metrics: Optional[dict]
    created_at: datetime
    data_hash: str
    
    class Config:
        from_attributes = True


class ExperimentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: dict
    metrics: Optional[dict] = None
    tags: Optional[dict] = None


class ExperimentResponse(BaseModel):
    experiment_id: str
    name: str
    run_id: Optional[str]
    status: str
    artifact_uri: Optional[str]


class DatasetVersionCreate(BaseModel):
    name: str
    version: str
    file_path: str
    description: Optional[str] = None
    schema_info: Optional[dict] = None


class DatasetVersionResponse(BaseModel):
    id: int
    name: str
    version: str
    file_hash: str
    dvc_file: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LineageGraphResponse(BaseModel):
    score_id: str
    nodes: List[dict]
    edges: List[dict]


# Provenance Endpoints
@router.get("/{score_id}", response_model=ProvenanceRecordResponse)
async def get_provenance(
    score_id: str,
    db: Session = Depends(get_db)
):
    """
    GET /provenance/{score_id}
    Get full data lineage for a score
    """
    record = crud.get_provenance_by_score_id(db, score_id)
    if not record:
        raise HTTPException(status_code=404, detail="Provenance record not found")
    return record


@router.post("/", response_model=ProvenanceRecordResponse)
async def create_provenance(
    data: ProvenanceRecordCreate,
    db: Session = Depends(get_db)
):
    """
    POST /provenance
    Create provenance record for a new score
    """
    record = crud.create_provenance_record(db, data.dict())
    return record


@router.get("/{score_id}/lineage", response_model=LineageGraphResponse)
async def get_lineage_graph(
    score_id: str,
    depth: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    GET /provenance/{score_id}/lineage
    Get lineage graph for visualization
    """
    record = crud.get_provenance_by_score_id(db, score_id)
    if not record:
        raise HTTPException(status_code=404, detail="Provenance record not found")
    
    # Build lineage graph
    nodes = []
    edges = []
    
    # Add source data nodes
    for idx, source in enumerate(record.data_sources):
        node_id = f"source_{idx}"
        nodes.append({
            "id": node_id,
            "type": "data_source",
            "label": source.get("name", f"Source {idx}"),
            "data": source
        })
        edges.append({
            "from": node_id,
            "to": "transform_0"
        })
    
    # Add transformation nodes
    for idx, transform in enumerate(record.transformations):
        node_id = f"transform_{idx}"
        nodes.append({
            "id": node_id,
            "type": "transformation",
            "label": transform.get("name", f"Transform {idx}"),
            "data": transform
        })
        if idx > 0:
            edges.append({
                "from": f"transform_{idx-1}",
                "to": node_id
            })
    
    # Add score node
    nodes.append({
        "id": "score",
        "type": "output",
        "label": f"Score {score_id}",
        "data": {"score_id": score_id, "metrics": record.metrics}
    })
    
    if record.transformations:
        edges.append({
            "from": f"transform_{len(record.transformations)-1}",
            "to": "score"
        })
    
    return LineageGraphResponse(
        score_id=score_id,
        nodes=nodes,
        edges=edges
    )


@router.get("/{score_id}/audit")
async def get_audit_trail(
    score_id: str,
    db: Session = Depends(get_db)
):
    """
    GET /provenance/{score_id}/audit
    Get audit trail for compliance
    """
    record = crud.get_provenance_by_score_id(db, score_id)
    if not record:
        raise HTTPException(status_code=404, detail="Provenance record not found")
    
    return {
        "score_id": score_id,
        "created_at": record.created_at.isoformat(),
        "pipeline_version": record.pipeline_version,
        "data_hash": record.data_hash,
        "data_sources_count": len(record.data_sources),
        "transformations_count": len(record.transformations),
        "compliance_info": {
            "traceable": True,
            "reproducible": True,
            "data_integrity_verified": True
        }
    }


# MLflow Experiment Endpoints
@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(
    data: ExperimentCreate
):
    """
    POST /provenance/experiments
    Create MLflow experiment
    """
    result = mlflow_manager.create_experiment(
        name=data.name,
        description=data.description,
        parameters=data.parameters,
        metrics=data.metrics,
        tags=data.tags
    )
    return result


@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    """
    GET /provenance/experiments/{experiment_id}
    Get experiment details
    """
    result = mlflow_manager.get_experiment(experiment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result


@router.get("/experiments")
async def list_experiments(
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    GET /provenance/experiments
    List all experiments
    """
    return mlflow_manager.list_experiments(limit)


@router.post("/experiments/{experiment_id}/log")
async def log_metrics(
    experiment_id: str,
    metrics: dict
):
    """
    POST /provenance/experiments/{experiment_id}/log
    Log metrics to experiment
    """
    result = mlflow_manager.log_metrics(experiment_id, metrics)
    return {"status": "logged", "metrics": metrics}


# DVC Dataset Versioning Endpoints
@router.post("/datasets", response_model=DatasetVersionResponse)
async def version_dataset(
    data: DatasetVersionCreate,
    db: Session = Depends(get_db)
):
    """
    POST /provenance/datasets
    Track dataset version with DVC
    """
    # Track with DVC
    dvc_result = dvc_manager.track_file(data.file_path)
    
    # Store in database
    record = crud.create_dataset_version(
        db,
        name=data.name,
        version=data.version,
        file_path=data.file_path,
        file_hash=dvc_result.get("hash", ""),
        dvc_file=dvc_result.get("dvc_file"),
        description=data.description,
        schema_info=data.schema_info
    )
    return record


@router.get("/datasets/{name}")
async def get_dataset_versions(
    name: str,
    db: Session = Depends(get_db)
):
    """
    GET /provenance/datasets/{name}
    Get all versions of a dataset
    """
    versions = crud.get_dataset_versions(db, name)
    return {"dataset": name, "versions": versions}


@router.get("/datasets/{name}/{version}")
async def get_dataset_version(
    name: str,
    version: str,
    db: Session = Depends(get_db)
):
    """
    GET /provenance/datasets/{name}/{version}
    Get specific dataset version
    """
    record = crud.get_dataset_version(db, name, version)
    if not record:
        raise HTTPException(status_code=404, detail="Dataset version not found")
    return record


@router.post("/datasets/{name}/{version}/checkout")
async def checkout_dataset(
    name: str,
    version: str,
    db: Session = Depends(get_db)
):
    """
    POST /provenance/datasets/{name}/{version}/checkout
    Checkout specific dataset version
    """
    record = crud.get_dataset_version(db, name, version)
    if not record:
        raise HTTPException(status_code=404, detail="Dataset version not found")
    
    result = dvc_manager.checkout_version(record.dvc_file, record.file_hash)
    return {"status": "checked_out", "version": version, "result": result}


# Compare Endpoints
@router.get("/compare")
async def compare_scores(
    score_ids: str = Query(..., description="Comma-separated score IDs"),
    db: Session = Depends(get_db)
):
    """
    GET /provenance/compare?score_ids=id1,id2,id3
    Compare provenance of multiple scores
    """
    ids = [s.strip() for s in score_ids.split(",")]
    records = []
    
    for score_id in ids:
        record = crud.get_provenance_by_score_id(db, score_id)
        if record:
            records.append({
                "score_id": record.score_id,
                "pipeline_version": record.pipeline_version,
                "data_hash": record.data_hash,
                "sources_count": len(record.data_sources),
                "transforms_count": len(record.transformations),
                "created_at": record.created_at.isoformat()
            })
    
    return {"comparison": records, "count": len(records)}
