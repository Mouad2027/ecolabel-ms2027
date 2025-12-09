"""
Score models for scoring service
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.connection import Base


class ScoreDB(Base):
    """SQLAlchemy model for eco-scores"""
    __tablename__ = "eco_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(50), nullable=True, index=True)
    lca_id = Column(String(50), nullable=True, index=True)
    score_numeric = Column(Float, nullable=False)
    score_letter = Column(String(1), nullable=False)
    explanation = Column(String(1000), nullable=True)
    confidence = Column(Float, default=0.0)
    breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic models

class ScoreCreate(BaseModel):
    """Pydantic model for creating score"""
    product_id: Optional[str] = None
    lca_id: Optional[str] = None
    score_numeric: float
    score_letter: str
    explanation: Optional[str] = None
    confidence: float = 0.0
    breakdown: Optional[Dict[str, Any]] = None


class Score(BaseModel):
    """Pydantic model for score (API response)"""
    id: Optional[str] = None
    score_numeric: float
    score_letter: str
    explanation: Optional[str] = None
    confidence: float = 0.0
    breakdown: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ScoreResponse(BaseModel):
    """Full response model for score"""
    id: str
    product_id: Optional[str] = None
    lca_id: Optional[str] = None
    score_numeric: float
    score_letter: str
    explanation: Optional[str] = None
    confidence: float = 0.0
    breakdown: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
