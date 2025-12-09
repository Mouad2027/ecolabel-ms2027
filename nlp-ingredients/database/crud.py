"""
CRUD operations for nlp-ingredients service
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from models.extraction import (
    ExtractionResultDB, 
    ExtractionResultCreate,
    IngredientTaxonomyDB,
    MaterialTaxonomyDB,
    LabelTaxonomyDB
)


def create_extraction(db: Session, extraction: ExtractionResultCreate) -> ExtractionResultDB:
    """
    Create a new extraction result record
    
    Args:
        db: Database session
        extraction: Extraction data
        
    Returns:
        Created extraction record
    """
    db_extraction = ExtractionResultDB(
        product_id=extraction.product_id,
        raw_text=extraction.raw_text,
        language=extraction.language,
        ingredients=extraction.ingredients,
        materials=extraction.materials,
        origins=extraction.origins,
        labels=extraction.labels,
        confidence=extraction.confidence
    )
    
    db.add(db_extraction)
    db.commit()
    db.refresh(db_extraction)
    
    return db_extraction


def get_extraction(db: Session, extraction_id: UUID) -> Optional[ExtractionResultDB]:
    """
    Get an extraction result by ID
    
    Args:
        db: Database session
        extraction_id: Extraction UUID
        
    Returns:
        Extraction record or None
    """
    return db.query(ExtractionResultDB).filter(ExtractionResultDB.id == extraction_id).first()


def get_extractions_by_product(
    db: Session, 
    product_id: str
) -> List[ExtractionResultDB]:
    """
    Get extraction results by product ID
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        List of extraction records
    """
    return db.query(ExtractionResultDB).filter(
        ExtractionResultDB.product_id == product_id
    ).all()


# Ingredient Taxonomy CRUD

def create_ingredient_taxonomy(
    db: Session,
    name: str,
    canonical_name: str = None,
    ecoinvent_id: str = None,
    category: str = None,
    synonyms: list = None,
    language: str = "en"
) -> IngredientTaxonomyDB:
    """Create a new ingredient taxonomy entry"""
    db_taxonomy = IngredientTaxonomyDB(
        name=name,
        canonical_name=canonical_name,
        ecoinvent_id=ecoinvent_id,
        category=category,
        synonyms=synonyms or [],
        language=language
    )
    
    db.add(db_taxonomy)
    db.commit()
    db.refresh(db_taxonomy)
    
    return db_taxonomy


def get_ingredient_by_name(db: Session, name: str) -> Optional[IngredientTaxonomyDB]:
    """Get ingredient taxonomy by name"""
    return db.query(IngredientTaxonomyDB).filter(
        IngredientTaxonomyDB.name == name.lower()
    ).first()


def search_ingredients(
    db: Session, 
    query: str, 
    limit: int = 10
) -> List[IngredientTaxonomyDB]:
    """Search ingredients by name"""
    return db.query(IngredientTaxonomyDB).filter(
        IngredientTaxonomyDB.name.ilike(f"%{query}%")
    ).limit(limit).all()


# Material Taxonomy CRUD

def create_material_taxonomy(
    db: Session,
    name: str,
    canonical_name: str = None,
    material_type: str = None,
    recyclable: str = None,
    ecoinvent_id: str = None
) -> MaterialTaxonomyDB:
    """Create a new material taxonomy entry"""
    db_taxonomy = MaterialTaxonomyDB(
        name=name,
        canonical_name=canonical_name,
        material_type=material_type,
        recyclable=recyclable,
        ecoinvent_id=ecoinvent_id
    )
    
    db.add(db_taxonomy)
    db.commit()
    db.refresh(db_taxonomy)
    
    return db_taxonomy


def get_material_by_name(db: Session, name: str) -> Optional[MaterialTaxonomyDB]:
    """Get material taxonomy by name"""
    return db.query(MaterialTaxonomyDB).filter(
        MaterialTaxonomyDB.name == name.lower()
    ).first()


# Label Taxonomy CRUD

def create_label_taxonomy(
    db: Session,
    name: str,
    label_type: str = None,
    keywords: list = None,
    description: str = None
) -> LabelTaxonomyDB:
    """Create a new label taxonomy entry"""
    db_taxonomy = LabelTaxonomyDB(
        name=name,
        label_type=label_type,
        keywords=keywords or [],
        description=description
    )
    
    db.add(db_taxonomy)
    db.commit()
    db.refresh(db_taxonomy)
    
    return db_taxonomy


def get_label_by_name(db: Session, name: str) -> Optional[LabelTaxonomyDB]:
    """Get label taxonomy by name"""
    return db.query(LabelTaxonomyDB).filter(
        LabelTaxonomyDB.name == name.lower()
    ).first()
