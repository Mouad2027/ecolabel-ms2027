"""
LCA result models for lca-lite service
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.connection import Base


class LCAResultDB(Base):
    """SQLAlchemy model for LCA results"""
    __tablename__ = "lca_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(50), nullable=True, index=True)
    co2 = Column(Float, nullable=False)  # kg CO2 equivalent
    water = Column(Float, nullable=False)  # liters
    energy = Column(Float, nullable=False)  # MJ
    breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic models

class LCAResultCreate(BaseModel):
    """Pydantic model for creating LCA result"""
    product_id: Optional[str] = None
    co2: float
    water: float
    energy: float
    breakdown: Optional[Dict[str, Any]] = None


class LCAResult(BaseModel):
    """Pydantic model for LCA result (API response)"""
    id: Optional[str] = None
    co2: float
    water: float
    energy: float
    breakdown: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class LCAResultResponse(BaseModel):
    """Full response model for LCA result"""
    id: str
    product_id: Optional[str] = None
    co2: float
    water: float
    energy: float
    breakdown: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
