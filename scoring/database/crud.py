"""
CRUD operations for scoring service
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from models.score import ScoreDB, ScoreCreate


def create_score(db: Session, score: ScoreCreate) -> ScoreDB:
    """
    Create a new score record
    
    Args:
        db: Database session
        score: Score data
        
    Returns:
        Created score record
    """
    db_score = ScoreDB(
        product_id=score.product_id,
        lca_id=score.lca_id,
        score_numeric=score.score_numeric,
        score_letter=score.score_letter,
        explanation=score.explanation,
        confidence=score.confidence,
        breakdown=score.breakdown
    )
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    
    return db_score


def get_score(db: Session, score_id: UUID) -> Optional[ScoreDB]:
    """
    Get a score by ID
    
    Args:
        db: Database session
        score_id: Score UUID
        
    Returns:
        Score record or None
    """
    return db.query(ScoreDB).filter(ScoreDB.id == score_id).first()


def get_scores_by_product(
    db: Session, 
    product_id: str
) -> List[ScoreDB]:
    """
    Get scores by product ID
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        List of score records
    """
    return db.query(ScoreDB).filter(
        ScoreDB.product_id == product_id
    ).order_by(ScoreDB.created_at.desc()).all()


def get_latest_score_by_product(
    db: Session, 
    product_id: str
) -> Optional[ScoreDB]:
    """
    Get the latest score for a product
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        Latest score record or None
    """
    return db.query(ScoreDB).filter(
        ScoreDB.product_id == product_id
    ).order_by(ScoreDB.created_at.desc()).first()


def get_scores(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[ScoreDB]:
    """
    Get list of scores with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of score records
    """
    return db.query(ScoreDB).offset(skip).limit(limit).all()


def get_scores_by_grade(
    db: Session, 
    grade: str,
    limit: int = 100
) -> List[ScoreDB]:
    """
    Get scores by letter grade
    
    Args:
        db: Database session
        grade: Letter grade (A-E)
        limit: Maximum number of records
        
    Returns:
        List of score records
    """
    return db.query(ScoreDB).filter(
        ScoreDB.score_letter == grade.upper()
    ).limit(limit).all()


def delete_score(db: Session, score_id: UUID) -> bool:
    """
    Delete a score
    
    Args:
        db: Database session
        score_id: Score UUID
        
    Returns:
        True if deleted, False if not found
    """
    db_score = get_score(db, score_id)
    
    if not db_score:
        return False
    
    db.delete(db_score)
    db.commit()
    
    return True
