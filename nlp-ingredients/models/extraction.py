"""
Extraction result models for nlp-ingredients service
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, String, Text, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.connection import Base


class ExtractionResultDB(Base):
    """SQLAlchemy model for extraction results"""
    __tablename__ = "extraction_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(50), nullable=True, index=True)
    raw_text = Column(Text, nullable=True)
    language = Column(String(10), default="en")
    ingredients = Column(JSON, default=list)
    materials = Column(JSON, default=list)
    origins = Column(JSON, default=list)
    labels = Column(JSON, default=list)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class IngredientTaxonomyDB(Base):
    """SQLAlchemy model for ingredient taxonomy"""
    __tablename__ = "ingredient_taxonomy"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    canonical_name = Column(String(255), nullable=True)
    ecoinvent_id = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    synonyms = Column(JSON, default=list)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MaterialTaxonomyDB(Base):
    """SQLAlchemy model for material taxonomy"""
    __tablename__ = "material_taxonomy"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    canonical_name = Column(String(255), nullable=True)
    material_type = Column(String(100), nullable=True)  # plastic, glass, metal, etc.
    recyclable = Column(String(50), nullable=True)  # yes, no, limited
    ecoinvent_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LabelTaxonomyDB(Base):
    """SQLAlchemy model for label/certification taxonomy"""
    __tablename__ = "label_taxonomy"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    label_type = Column(String(100), nullable=True)  # environmental, health, quality
    keywords = Column(JSON, default=list)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic models

class ExtractionResultCreate(BaseModel):
    """Pydantic model for creating extraction result"""
    product_id: Optional[str] = None
    raw_text: Optional[str] = None
    language: str = "en"
    ingredients: List = []
    materials: List = []
    origins: List = []
    labels: List = []
    confidence: float = 0.0


class ExtractionResult(BaseModel):
    """Pydantic model for extraction result (API response)"""
    id: Optional[str] = None
    ingredients: List = []
    materials: List = []
    origins: List = []
    labels: List = []
    confidence: float = 0.0
    
    class Config:
        from_attributes = True


class IngredientMapped(BaseModel):
    """Pydantic model for mapped ingredient"""
    name: str
    normalized_name: Optional[str] = None
    percentage: Optional[float] = None
    ecoinvent_id: Optional[str] = None
    category: Optional[str] = None
    unit: str = "kg"
    mapped: bool = False
