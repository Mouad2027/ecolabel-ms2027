"""
Product models for widget-api backend
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.connection import Base


class ProductDB(Base):
    """SQLAlchemy model for products with scores"""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=True)
    brand = Column(String(255), nullable=True)
    gtin = Column(String(14), nullable=True, unique=True, index=True)
    
    # Score data
    score_id = Column(String(50), nullable=True)
    score_letter = Column(String(1), nullable=True, index=True)
    score_numeric = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # LCA indicators
    co2 = Column(Float, nullable=True)
    water = Column(Float, nullable=True)
    energy = Column(Float, nullable=True)
    
    # Extracted data
    ingredients = Column(JSON, default=list)
    origins = Column(JSON, default=list)
    labels = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic models

class ProductCreate(BaseModel):
    """Pydantic model for creating product"""
    title: Optional[str] = None
    brand: Optional[str] = None
    gtin: Optional[str] = None
    score_id: Optional[str] = None
    score_letter: Optional[str] = None
    score_numeric: Optional[float] = None
    confidence: Optional[float] = None
    co2: Optional[float] = None
    water: Optional[float] = None
    energy: Optional[float] = None
    ingredients: Optional[List] = []
    origins: Optional[List] = []
    labels: Optional[List] = []


class ProductResponse(BaseModel):
    """Pydantic model for product response"""
    id: str
    title: Optional[str] = None
    brand: Optional[str] = None
    gtin: Optional[str] = None
    eco_score: dict
    breakdown: dict
    ingredients: List = []
    origins: List = []
    labels: List = []
    provenance_url: Optional[str] = None
    last_updated: Optional[str] = None
    
    class Config:
        from_attributes = True
