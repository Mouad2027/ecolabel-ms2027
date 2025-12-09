"""
API routes for eco-score computation
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import uuid

from ml.score_normalizer import ScoreNormalizer
from ml.score_calculator import ScoreCalculator
from database.connection import get_db
from database.crud import create_score, get_score, get_scores_by_product
from models.score import ScoreCreate

router = APIRouter()

# Initialize ML components
score_normalizer = ScoreNormalizer()
score_calculator = ScoreCalculator()


class LCAIndicators(BaseModel):
    """Input model for LCA indicators"""
    co2: float  # kg CO2 equivalent
    water: float  # liters
    energy: float  # MJ
    product_id: Optional[str] = None
    lca_id: Optional[str] = None


class BonusMalus(BaseModel):
    """Bonus/malus adjustments"""
    bio_certified: bool = False
    recyclable_packaging: bool = False
    local_sourcing: bool = False
    fair_trade: bool = False
    endangered_species: bool = False
    deforestation_risk: bool = False


class ScoreRequest(BaseModel):
    """Request model for score computation"""
    indicators: LCAIndicators
    bonus_malus: Optional[BonusMalus] = None
    product_weight_kg: Optional[float] = 1.0


class ScoreResponse(BaseModel):
    """Response model for eco-score"""
    id: Optional[str] = None
    score_numeric: float
    score_letter: str  # A, B, C, D, E
    explanation: str
    confidence: float
    breakdown: Optional[dict] = None


@router.post("/compute", response_model=ScoreResponse)
async def compute_score(
    request: ScoreRequest,
    db: Session = Depends(get_db)
):
    """
    Compute eco-score from LCA indicators
    
    Input: LCA indicators (CO2, water, energy)
    Output: Score numeric (0-100), letter grade (A-E), explanation
    """
    try:
        # Normalize indicators per kg of product
        weight = request.product_weight_kg or 1.0
        
        normalized_indicators = score_normalizer.normalize(
            co2=request.indicators.co2 / weight,
            water=request.indicators.water / weight,
            energy=request.indicators.energy / weight
        )
        
        # Calculate base score
        base_score = score_calculator.calculate_weighted_score(
            normalized_co2=normalized_indicators["co2_normalized"],
            normalized_water=normalized_indicators["water_normalized"],
            normalized_energy=normalized_indicators["energy_normalized"]
        )
        
        # Apply bonus/malus adjustments
        adjusted_score = base_score
        adjustments = []
        
        if request.bonus_malus:
            adjustment_result = score_calculator.apply_bonus_malus(
                base_score=base_score,
                bio_certified=request.bonus_malus.bio_certified,
                recyclable_packaging=request.bonus_malus.recyclable_packaging,
                local_sourcing=request.bonus_malus.local_sourcing,
                fair_trade=request.bonus_malus.fair_trade,
                endangered_species=request.bonus_malus.endangered_species,
                deforestation_risk=request.bonus_malus.deforestation_risk
            )
            adjusted_score = adjustment_result["adjusted_score"]
            adjustments = adjustment_result["adjustments"]
        
        # Convert to letter grade
        letter_grade = score_calculator.numeric_to_letter(adjusted_score)
        
        # Generate explanation
        explanation = score_calculator.generate_explanation(
            score=adjusted_score,
            letter=letter_grade,
            normalized_indicators=normalized_indicators,
            adjustments=adjustments
        )
        
        # Calculate confidence
        confidence = score_normalizer.calculate_confidence(normalized_indicators)
        
        result = {
            "score_numeric": round(adjusted_score, 2),
            "score_letter": letter_grade,
            "explanation": explanation,
            "confidence": round(confidence, 2),
            "breakdown": {
                "base_score": round(base_score, 2),
                "adjusted_score": round(adjusted_score, 2),
                "normalized_indicators": normalized_indicators,
                "adjustments": adjustments,
                "weights": score_calculator.get_weights()
            }
        }
        
        # Store score in database
        score_data = ScoreCreate(
            product_id=request.indicators.product_id,
            lca_id=request.indicators.lca_id,
            score_numeric=result["score_numeric"],
            score_letter=result["score_letter"],
            explanation=result["explanation"],
            confidence=result["confidence"],
            breakdown=result["breakdown"]
        )
        
        db_score = create_score(db, score_data)
        result["id"] = str(db_score.id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Score computation error: {str(e)}")


@router.get("/result/{score_id}")
async def get_score_by_id(
    score_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a previous score by ID"""
    try:
        score_uuid = uuid.UUID(score_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid score ID format")
    
    score = get_score(db, score_uuid)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return {
        "id": str(score.id),
        "product_id": score.product_id,
        "score_numeric": score.score_numeric,
        "score_letter": score.score_letter,
        "explanation": score.explanation,
        "confidence": score.confidence,
        "breakdown": score.breakdown,
        "created_at": score.created_at.isoformat()
    }


@router.get("/product/{product_id}")
async def get_scores_for_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get all scores for a product"""
    scores = get_scores_by_product(db, product_id)
    
    return {
        "product_id": product_id,
        "scores": [
            {
                "id": str(s.id),
                "score_numeric": s.score_numeric,
                "score_letter": s.score_letter,
                "confidence": s.confidence,
                "created_at": s.created_at.isoformat()
            }
            for s in scores
        ]
    }


@router.get("/thresholds")
async def get_score_thresholds():
    """Get score thresholds for letter grades"""
    return {
        "thresholds": score_calculator.get_thresholds(),
        "weights": score_calculator.get_weights(),
        "description": {
            "A": "Excellent - Very low environmental impact",
            "B": "Good - Low environmental impact",
            "C": "Average - Moderate environmental impact",
            "D": "Poor - High environmental impact",
            "E": "Very Poor - Very high environmental impact"
        }
    }
