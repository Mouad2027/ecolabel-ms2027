"""
CRUD operations for widget-api backend
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.product import ProductDB, ProductCreate


def get_product_with_score(db: Session, product_id: str) -> Optional[ProductDB]:
    """
    Get a product with its score by ID
    
    Args:
        db: Database session
        product_id: Product ID (UUID string)
        
    Returns:
        Product record or None
    """
    try:
        product_uuid = UUID(product_id)
        return db.query(ProductDB).filter(ProductDB.id == product_uuid).first()
    except ValueError:
        return None


def get_product_by_gtin(db: Session, gtin: str) -> Optional[ProductDB]:
    """
    Get a product by GTIN/EAN code
    
    Args:
        db: Database session
        gtin: GTIN/EAN code
        
    Returns:
        Product record or None
    """
    return db.query(ProductDB).filter(ProductDB.gtin == gtin).first()


def search_products(
    db: Session, 
    query: str, 
    limit: int = 10
) -> List[ProductDB]:
    """
    Search products by title or brand
    
    Args:
        db: Database session
        query: Search query
        limit: Maximum number of results
        
    Returns:
        List of matching products
    """
    search_pattern = f"%{query}%"
    
    return db.query(ProductDB).filter(
        or_(
            ProductDB.title.ilike(search_pattern),
            ProductDB.brand.ilike(search_pattern),
            ProductDB.gtin.like(search_pattern)
        )
    ).limit(limit).all()


def create_or_update_product(
    db: Session, 
    product: ProductCreate
) -> ProductDB:
    """
    Create or update a product
    
    Args:
        db: Database session
        product: Product data
        
    Returns:
        Created/updated product record
    """
    # Check if product exists by GTIN
    existing = None
    if product.gtin:
        existing = get_product_by_gtin(db, product.gtin)
    
    if existing:
        # Update existing product
        for field, value in product.dict(exclude_unset=True).items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new product
        db_product = ProductDB(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product


def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[ProductDB]:
    """
    Get list of products with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of product records
    """
    return db.query(ProductDB).offset(skip).limit(limit).all()


def get_products_by_score(
    db: Session,
    score_letter: str,
    limit: int = 50
) -> List[ProductDB]:
    """
    Get products by score letter
    
    Args:
        db: Database session
        score_letter: Score letter (A-E)
        limit: Maximum number of results
        
    Returns:
        List of products with the given score
    """
    return db.query(ProductDB).filter(
        ProductDB.score_letter == score_letter.upper()
    ).limit(limit).all()


def delete_product(db: Session, product_id: UUID) -> bool:
    """
    Delete a product
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        True if deleted, False if not found
    """
    product = get_product_with_score(db, str(product_id))
    
    if not product:
        return False
    
    db.delete(product)
    db.commit()
    
    return True
