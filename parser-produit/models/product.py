"""
Product models for parser-produit service
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.connection import Base


class ProductParsedDB(Base):
    """SQLAlchemy model for parsed products"""
    __tablename__ = "parsed_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=True)
    file_type = Column(String(50), nullable=True)
    title = Column(String(500), nullable=True)
    brand = Column(String(255), nullable=True)
    ingredients_text = Column(Text, nullable=True)
    packaging = Column(String(500), nullable=True)
    origin = Column(String(255), nullable=True)
    gtin = Column(String(14), nullable=True, index=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductParsedCreate(BaseModel):
    """Pydantic model for creating parsed product"""
    filename: Optional[str] = None
    file_type: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    ingredients_text: Optional[str] = None
    packaging: Optional[str] = None
    origin: Optional[str] = None
    gtin: Optional[str] = None
    raw_text: Optional[str] = None


class ProductParsed(BaseModel):
    """Pydantic model for parsed product (API response)"""
    id: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    ingredients_text: Optional[str] = None
    packaging: Optional[str] = None
    origin: Optional[str] = None
    gtin: Optional[str] = None
    raw_text: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductParsedResponse(BaseModel):
    """Full response model for parsed product"""
    id: str
    filename: Optional[str] = None
    file_type: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    ingredients_text: Optional[str] = None
    packaging: Optional[str] = None
    origin: Optional[str] = None
    gtin: Optional[str] = None
    raw_text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
