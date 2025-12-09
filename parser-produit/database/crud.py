"""
CRUD operations for parser-produit service
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.product import ProductParsedDB, ProductParsedCreate


def create_parsed_product(db: Session, product: ProductParsedCreate) -> ProductParsedDB:
    """
    Create a new parsed product record
    
    Args:
        db: Database session
        product: Product data
        
    Returns:
        Created product record
    """
    db_product = ProductParsedDB(
        filename=product.filename,
        file_type=product.file_type,
        title=product.title,
        brand=product.brand,
        ingredients_text=product.ingredients_text,
        packaging=product.packaging,
        origin=product.origin,
        gtin=product.gtin,
        raw_text=product.raw_text
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


def get_parsed_product(db: Session, product_id: UUID) -> Optional[ProductParsedDB]:
    """
    Get a parsed product by ID
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        Product record or None
    """
    return db.query(ProductParsedDB).filter(ProductParsedDB.id == product_id).first()


def get_parsed_product_by_gtin(db: Session, gtin: str) -> Optional[ProductParsedDB]:
    """
    Get a parsed product by GTIN
    
    Args:
        db: Database session
        gtin: Product GTIN
        
    Returns:
        Product record or None
    """
    return db.query(ProductParsedDB).filter(ProductParsedDB.gtin == gtin).first()


def get_parsed_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[ProductParsedDB]:
    """
    Get list of parsed products with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of product records
    """
    return db.query(ProductParsedDB).offset(skip).limit(limit).all()


def update_parsed_product(
    db: Session, 
    product_id: UUID, 
    product: ProductParsedCreate
) -> Optional[ProductParsedDB]:
    """
    Update a parsed product
    
    Args:
        db: Database session
        product_id: Product UUID
        product: Updated product data
        
    Returns:
        Updated product record or None
    """
    db_product = get_parsed_product(db, product_id)
    
    if not db_product:
        return None
    
    update_data = product.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


def delete_parsed_product(db: Session, product_id: UUID) -> bool:
    """
    Delete a parsed product
    
    Args:
        db: Database session
        product_id: Product UUID
        
    Returns:
        True if deleted, False if not found
    """
    db_product = get_parsed_product(db, product_id)
    
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    
    return True


def get_parsing_stats(db: Session) -> Dict[str, Any]:
    """
    Get parsing statistics
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with parsing statistics
    """
    total_count = db.query(func.count(ProductParsedDB.id)).scalar()
    
    # Count by file type
    file_type_stats = db.query(
        ProductParsedDB.file_type,
        func.count(ProductParsedDB.id)
    ).group_by(ProductParsedDB.file_type).all()
    
    # Count products with GTIN
    gtin_count = db.query(func.count(ProductParsedDB.id)).filter(
        ProductParsedDB.gtin.isnot(None),
        ProductParsedDB.gtin != ''
    ).scalar()
    
    # Count products with ingredients
    ingredients_count = db.query(func.count(ProductParsedDB.id)).filter(
        ProductParsedDB.ingredients_text.isnot(None),
        ProductParsedDB.ingredients_text != ''
    ).scalar()
    
    return {
        "total_products": total_count or 0,
        "by_file_type": {ft: count for ft, count in file_type_stats} if file_type_stats else {},
        "products_with_gtin": gtin_count or 0,
        "products_with_ingredients": ingredients_count or 0
    }
