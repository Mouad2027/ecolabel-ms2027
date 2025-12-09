"""
CRUD operations for lca-lite service
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from models.lca import LCAResultDB, LCAResultCreate


def create_lca_result(db: Session, lca_result: LCAResultCreate) -> LCAResultDB:
    """
    Create a new LCA result record
    
    Args:
        db: Database session
        lca_result: LCA result data
        
    Returns:
        Created LCA result record
    """
    db_result = LCAResultDB(
        product_id=lca_result.product_id,
        co2=lca_result.co2,
        water=lca_result.water,
        energy=lca_result.energy,
        breakdown=lca_result.breakdown
    )
    
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return db_result


def get_lca_result(db: Session, result_id: UUID) -> Optional[LCAResultDB]:
    """
    Get an LCA result by ID
    
    Args:
        db: Database session
        result_id: Result UUID
        
    Returns:
        LCA result record or None
    """
    return db.query(LCAResultDB).filter(LCAResultDB.id == result_id).first()


def get_lca_results_by_product(
    db: Session, 
    product_id: str
) -> List[LCAResultDB]:
    """
    Get LCA results by product ID
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        List of LCA result records
    """
    return db.query(LCAResultDB).filter(
        LCAResultDB.product_id == product_id
    ).all()


def get_latest_lca_result_by_product(
    db: Session, 
    product_id: str
) -> Optional[LCAResultDB]:
    """
    Get the latest LCA result for a product
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        Latest LCA result record or None
    """
    return db.query(LCAResultDB).filter(
        LCAResultDB.product_id == product_id
    ).order_by(LCAResultDB.created_at.desc()).first()


def get_lca_results(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[LCAResultDB]:
    """
    Get list of LCA results with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of LCA result records
    """
    return db.query(LCAResultDB).offset(skip).limit(limit).all()


def delete_lca_result(db: Session, result_id: UUID) -> bool:
    """
    Delete an LCA result
    
    Args:
        db: Database session
        result_id: Result UUID
        
    Returns:
        True if deleted, False if not found
    """
    db_result = get_lca_result(db, result_id)
    
    if not db_result:
        return False
    
    db.delete(db_result)
    db.commit()
    
    return True
