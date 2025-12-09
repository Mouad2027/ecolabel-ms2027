"""
API routes for NLP extraction
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import uuid

from nlp.spacy_pipeline import SpacyPipeline
from nlp.bert_classifier import BertClassifier
from nlp.ingredient_mapper import IngredientMapper
from models.extraction import ExtractionResult, ExtractionResultCreate
from database.connection import get_db
from database.crud import create_extraction, get_extraction

router = APIRouter()

# Initialize NLP components
spacy_pipeline = SpacyPipeline()
bert_classifier = BertClassifier()
ingredient_mapper = IngredientMapper()


class ExtractRequest(BaseModel):
    """Request model for NLP extraction"""
    text: str
    language: Optional[str] = "en"
    product_id: Optional[str] = None


class ExtractResponse(BaseModel):
    """Response model for NLP extraction"""
    id: Optional[str] = None
    ingredients: list
    materials: list
    origins: list
    labels: list
    confidence: Optional[float] = None


@router.post("/extract", response_model=ExtractResponse)
async def extract_entities(
    request: ExtractRequest,
    db: Session = Depends(get_db)
):
    """
    Extract and normalize entities from raw text
    
    Returns:
    - ingredients: List of extracted ingredients
    - materials: List of packaging materials
    - origins: List of geographical origins
    - labels: List of labels (bio, recyclable, etc.)
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Step 1: Extract entities using spaCy
        spacy_results = spacy_pipeline.extract_entities(
            request.text, 
            language=request.language
        )
        
        # Step 2: Classify and enhance with BERT
        bert_results = bert_classifier.classify_entities(
            request.text,
            spacy_results
        )
        
        # Step 3: Map ingredients to EcoInvent taxonomy
        mapped_ingredients = ingredient_mapper.map_to_ecoinvent(
            bert_results.get("ingredients", [])
        )
        
        # Combine results
        result = {
            "ingredients": mapped_ingredients,
            "materials": bert_results.get("materials", []),
            "origins": bert_results.get("origins", []),
            "labels": bert_results.get("labels", []),
            "confidence": bert_results.get("confidence", 0.0)
        }
        
        # Store extraction result in database
        extraction_data = ExtractionResultCreate(
            product_id=request.product_id,
            raw_text=request.text,
            language=request.language,
            ingredients=result["ingredients"],
            materials=result["materials"],
            origins=result["origins"],
            labels=result["labels"],
            confidence=result["confidence"]
        )
        
        db_extraction = create_extraction(db, extraction_data)
        result["id"] = str(db_extraction.id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP extraction error: {str(e)}")


@router.get("/extraction/{extraction_id}")
async def get_extraction_by_id(
    extraction_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a previous extraction result by ID"""
    try:
        extraction_uuid = uuid.UUID(extraction_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid extraction ID format")
    
    extraction = get_extraction(db, extraction_uuid)
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    return {
        "id": str(extraction.id),
        "product_id": extraction.product_id,
        "ingredients": extraction.ingredients,
        "materials": extraction.materials,
        "origins": extraction.origins,
        "labels": extraction.labels,
        "confidence": extraction.confidence,
        "created_at": extraction.created_at.isoformat()
    }


@router.post("/batch-extract")
async def batch_extract(
    texts: list[str],
    db: Session = Depends(get_db)
):
    """
    Batch extract entities from multiple texts
    """
    results = []
    
    for text in texts:
        try:
            spacy_results = spacy_pipeline.extract_entities(text)
            bert_results = bert_classifier.classify_entities(text, spacy_results)
            mapped_ingredients = ingredient_mapper.map_to_ecoinvent(
                bert_results.get("ingredients", [])
            )
            
            results.append({
                "ingredients": mapped_ingredients,
                "materials": bert_results.get("materials", []),
                "origins": bert_results.get("origins", []),
                "labels": bert_results.get("labels", []),
                "confidence": bert_results.get("confidence", 0.0)
            })
        except Exception as e:
            results.append({
                "error": str(e),
                "ingredients": [],
                "materials": [],
                "origins": [],
                "labels": []
            })
    
    return {"results": results}
