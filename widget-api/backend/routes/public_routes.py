"""
Public API routes for widget
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
import httpx
import os
import logging

from database.connection import get_db
from database.crud import (
    get_product_with_score, 
    search_products, 
    get_product_by_gtin,
    create_or_update_product
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Service URLs from environment
PARSER_SERVICE = os.getenv("PARSER_SERVICE_URL", "http://parser-produit:8001")
NLP_SERVICE = os.getenv("NLP_SERVICE_URL", "http://nlp-ingredients:8002")
LCA_SERVICE = os.getenv("LCA_SERVICE_URL", "http://lca-lite:8003")
SCORING_SERVICE = os.getenv("SCORING_SERVICE_URL", "http://scoring:8004")
PROVENANCE_SERVICE = os.getenv("PROVENANCE_SERVICE_URL", "http://provenance:8006")


@router.get("/history")
async def get_products_history(
    limit: int = Query(50, ge=1, le=100, description="Nombre de produits à retourner"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination"),
    db: Session = Depends(get_db)
):
    """
    Récupérer l'historique des produits analysés
    
    Args:
        limit: Nombre maximum de produits à retourner
        offset: Décalage pour la pagination
        db: Database session
        
    Returns:
        Liste des produits avec leurs éco-scores
    """
    try:
        from models.product import ProductDB
        
        # Récupérer les produits triés par date de création (plus récent d'abord)
        products = db.query(ProductDB)\
            .order_by(ProductDB.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        # Compter le total de produits
        total = db.query(ProductDB).count()
        
        # Formater les résultats
        results = []
        for product in products:
            # Obtenir l'origine depuis le JSON origins s'il existe
            origin = None
            if product.origins and len(product.origins) > 0:
                origin = product.origins[0] if isinstance(product.origins, list) else str(product.origins)
            
            # Déterminer la couleur du score
            score_color = None
            if product.score_letter:
                score_colors = {"A": "#27ae60", "B": "#2ecc71", "C": "#f39c12", "D": "#e67e22", "E": "#e74c3c"}
                score_color = score_colors.get(product.score_letter, "#95a5a6")
            
            results.append({
                "id": str(product.id),
                "title": product.title,
                "brand": product.brand,
                "gtin": product.gtin,
                "origin": origin,
                "eco_score": {
                    "letter": product.score_letter,
                    "numeric": product.score_numeric,
                    "color": score_color,
                    "confidence": product.confidence
                } if product.score_letter else None,
                "impacts": {
                    "co2": product.co2,
                    "water": product.water,
                    "energy": product.energy
                } if product.co2 is not None else None,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            })
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(results),
            "products": results
        }
        
    except Exception as e:
        logger.error(f"Error fetching products history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

# Local fallback impact factors for when services are unavailable
LOCAL_CO2_FACTORS = {
    "glucose": 0.8, "vegetable oil": 3.0, "oil": 3.0, "vegetable": 0.5,
    "milk": 1.3, "milk powder": 10.4, "skimmed milk": 1.1, "whole milk": 1.4,
    "sugar": 0.6, "cocoa": 4.5, "cocoa butter": 5.0, "cocoa mass": 4.8, "cocoa powder": 4.5,
    "whey": 1.0, "whey powder": 8.0, "lactose": 1.2,
    "butter": 8.5, "butter oil": 9.0, "milk fat": 8.5, "milk protein": 8.0,
    "emulsifier": 2.0, "soya": 0.4, "soya lecithin": 1.5, "lecithin": 1.5,
    "flavouring": 2.0, "flavoring": 2.0, "natural flavouring": 1.5,
    "salt": 0.1, "sodium": 0.1, "bicarbonate": 0.5,
    "flour": 0.8, "wheat flour": 0.8, "wheat": 0.8, "wheat starch": 0.9,
    "barley": 0.6, "barley flour": 0.7, "malt": 1.0, "barley malt": 1.0,
    "egg": 3.0, "egg white": 2.5, "egg yolk": 3.5, "egg powder": 8.0,
    "dextrose": 0.7, "gluten": 1.2, "wheat gluten": 1.2,
    "yeast": 1.5, "carbonate": 0.5,
    "caramelised sugar": 1.2, "caramel": 1.2, "invert sugar": 0.7,
    "thickener": 1.0, "guar gum": 1.5, "stabiliser": 1.0, "phosphate": 0.8,
    "colour": 2.0, "carotene": 3.0, "vanilla": 5.0, "raising agent": 0.8,
}

LOCAL_WATER_FACTORS = {
    "glucose": 1200, "vegetable oil": 5000, "oil": 5000, "vegetable": 300,
    "milk": 1020, "milk powder": 8000, "skimmed milk": 950, "whole milk": 1100,
    "sugar": 1782, "cocoa": 27000, "cocoa butter": 25000, "cocoa mass": 26000, "cocoa powder": 27000,
    "whey": 800, "whey powder": 6000, "lactose": 900,
    "butter": 5550, "butter oil": 5800, "milk fat": 5500, "milk protein": 5200,
    "flour": 1827, "wheat flour": 1827, "wheat": 1827, "wheat starch": 1900,
    "egg": 3300, "egg white": 2800, "egg yolk": 3500, "egg powder": 10000,
    "chocolate": 17196, "salt": 50, "vanilla": 12600,
}

LOCAL_ENERGY_FACTORS = {
    "glucose": 4.0, "vegetable oil": 8.0, "oil": 8.0, "vegetable": 2.0,
    "milk": 2.5, "milk powder": 15.0, "sugar": 5.5,
    "cocoa": 25.0, "cocoa butter": 22.0, "cocoa mass": 23.0, "cocoa powder": 24.0,
    "flour": 3.5, "wheat flour": 3.5, "wheat": 3.5,
    "egg": 6.0, "chocolate": 15.0, "butter": 8.0,
}

def calculate_local_lca(ingredients_text: str) -> dict:
    """Calculate LCA impacts locally when services are unavailable"""
    if not ingredients_text:
        return {"co2": 0, "water": 0, "energy": 0}
    
    # Parse ingredients (simple split)
    text = ingredients_text.lower()
    # Remove parentheses content for cleaner matching
    import re
    text = re.sub(r'\([^)]*\)', '', text)
    
    total_co2 = 0.0
    total_water = 0.0
    total_energy = 0.0
    matched_count = 0
    
    # Try to match ingredients from our local factors
    for ingredient, co2_factor in LOCAL_CO2_FACTORS.items():
        if ingredient in text:
            # Weight decreases by position (first ingredients = more important)
            weight = 0.15 if matched_count < 3 else 0.08 if matched_count < 6 else 0.03
            total_co2 += co2_factor * weight
            total_water += LOCAL_WATER_FACTORS.get(ingredient, 500) * weight
            total_energy += LOCAL_ENERGY_FACTORS.get(ingredient, 5.0) * weight
            matched_count += 1
    
    # Add baseline if nothing matched
    if matched_count == 0:
        total_co2 = 2.0
        total_water = 1500
        total_energy = 8.0
    
    return {
        "co2": round(total_co2, 2),
        "water": round(total_water, 0),
        "energy": round(total_energy, 2)
    }

def calculate_local_score(co2: float, water: float, energy: float) -> dict:
    """Calculate eco-score locally based on LCA impacts"""
    # Normalize values (based on typical ranges)
    # CO2: 0-10 kg → 0-100 score
    co2_score = min(100, (co2 / 10) * 100)
    # Water: 0-10000 L → 0-100 score
    water_score = min(100, (water / 10000) * 100)
    # Energy: 0-30 MJ → 0-100 score
    energy_score = min(100, (energy / 30) * 100)
    
    # Weighted average (CO2 = 50%, water = 30%, energy = 20%)
    numeric_score = co2_score * 0.5 + water_score * 0.3 + energy_score * 0.2
    numeric_score = round(numeric_score)
    
    # Convert to letter grade
    if numeric_score < 20:
        letter = "A"
    elif numeric_score < 40:
        letter = "B"
    elif numeric_score < 60:
        letter = "C"
    elif numeric_score < 80:
        letter = "D"
    else:
        letter = "E"
    
    return {
        "score_letter": letter,
        "score_numeric": numeric_score,
        "confidence": 0.75
    }


@router.get("/product/{product_id}")
async def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Get product details with eco-score
    
    Returns:
    - Product details
    - Eco-score letter
    - Breakdown (CO2, water, energy)
    - Origins and ingredients
    - Provenance link
    """
    product = get_product_with_score(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Build response
    response = {
        "id": str(product.id),
        "title": product.title,
        "brand": product.brand,
        "gtin": product.gtin,
        "weight_g": product.weight_g,
        "eco_score": {
            "letter": product.score_letter,
            "numeric": product.score_numeric,
            "color": get_score_color(product.score_letter),
            "confidence": product.confidence
        },
        "breakdown": {
            "co2": {
                "value": product.co2,
                "unit": "kg CO2e",
                "label": "Carbon Footprint"
            },
            "water": {
                "value": product.water,
                "unit": "L",
                "label": "Water Usage"
            },
            "energy": {
                "value": product.energy,
                "unit": "MJ",
                "label": "Energy Consumption"
            }
        },
        "ingredients": product.ingredients or [],
        "origins": product.origins or [],
        "labels": product.labels or [],
        "provenance_url": f"/public/provenance/{product.score_id}" if product.score_id else None,
        "last_updated": product.updated_at.isoformat() if product.updated_at else None
    }
    
    return response


@router.get("/product/gtin/{gtin}")
async def get_product_by_gtin_code(
    gtin: str,
    db: Session = Depends(get_db)
):
    """Get product by GTIN/EAN code"""
    product = get_product_by_gtin(db, gtin)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return await get_product(str(product.id), db)


@router.get("/products/search")
async def search_products_endpoint(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search products by name or brand"""
    products = search_products(db, q, limit)
    
    return {
        "query": q,
        "count": len(products),
        "results": [
            {
                "id": str(p.id),
                "title": p.title,
                "brand": p.brand,
                "gtin": p.gtin,
                "eco_score": {
                    "letter": p.score_letter,
                    "color": get_score_color(p.score_letter)
                }
            }
            for p in products
        ]
    }


@router.get("/score/{score_id}")
async def get_score_details(score_id: str):
    """Get detailed score information"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SCORING_SERVICE}/score/result/{score_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Score not found"
                )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Scoring service unavailable")


@router.get("/provenance/{score_id}")
async def get_provenance(score_id: str):
    """Get provenance/lineage information for a score"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{PROVENANCE_SERVICE}/provenance/{score_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "score_id": score_id,
                    "message": "Provenance data not available"
                }
    except httpx.RequestError:
        return {
            "score_id": score_id,
            "message": "Provenance service unavailable"
        }


@router.post("/products/upload")
async def upload_and_analyze_product(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file (image, PDF, HTML) and analyze it to extract product info and calculate eco-score.
    This endpoint proxies to the parser service and then calculates the eco-score.
    
    Args:
        file: The uploaded file (image, PDF, HTML, or text)
        db: Database session
        
    Returns:
        Product data with eco-score
    """
    logger.info(f"Received file upload: {file.filename}, content_type: {file.content_type}")
    
    try:
        # Step 1: Send file to parser service
        file_content = await file.read()
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {"file": (file.filename, file_content, file.content_type)}
            
            parser_response = await client.post(
                f"{PARSER_SERVICE}/product/parse",
                files=files
            )
            
            if parser_response.status_code != 200:
                logger.error(f"Parser service error: {parser_response.status_code} - {parser_response.text}")
                raise HTTPException(
                    status_code=parser_response.status_code,
                    detail=f"Parser service error: {parser_response.text}"
                )
            
            parsed_data = parser_response.json()
            logger.info(f"Parsed product data: {parsed_data.get('title', 'Unknown')}")
        
        # Step 2: Create product and calculate score using existing endpoint logic
        product_data = {
            "title": parsed_data.get("title", "Produit sans nom"),
            "brand": parsed_data.get("brand", ""),
            "gtin": parsed_data.get("gtin", ""),
            "ingredients_text": parsed_data.get("ingredients_text", ""),
            "origin": parsed_data.get("origin", ""),
            "packaging": parsed_data.get("packaging", ""),
            "weight_g": parsed_data.get("weight_g"),  # Product weight in grams
            "serving_size": parsed_data.get("serving_size")
        }
        
        logger.info(f"Creating product with data: {product_data}")
        
        # Call the existing product creation logic (pass db directly, not via Depends)
        try:
            result = await _create_product_and_score_internal(product_data, db)
        except Exception as create_error:
            logger.error(f"Error in create_product_and_score: {create_error}", exc_info=True)
            # Return basic result even if scoring fails
            result = {
                "id": None,
                "title": product_data.get("title"),
                "brand": product_data.get("brand"),
                "gtin": product_data.get("gtin"),
                "weight_g": product_data.get("weight_g"),
                "eco_score": {"letter": "E", "numeric": 80, "color": "#E74C3C", "confidence": 0.3},
                "breakdown": {"co2": {"value": 0}, "water": {"value": 0}, "energy": {"value": 0}},
                "ingredients": [],
                "error": str(create_error)
            }
        
        # Add parsed data to result
        result["parsed_data"] = parsed_data
        
        return result
        
    except httpx.RequestError as e:
        logger.error(f"HTTP error during file upload processing: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing file upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/products")
async def create_product_and_score(
    product_data: dict,
    db: Session = Depends(get_db)
):
    """
    Create/update product and calculate eco-score (HTTP endpoint)
    """
    return await _create_product_and_score_internal(product_data, db)


async def _create_product_and_score_internal(
    product_data: dict,
    db: Session
):
    """
    Internal function to create/update product and calculate eco-score
    
    Expected input:
    {
        "title": "Product name",
        "brand": "Brand name",
        "gtin": "1234567890123",
        "ingredients_text": "ingredient1, ingredient2...",
        "origin": "Country/Region",
        "packaging": "packaging type"
    }
    
    Returns the product with calculated eco-score
    """
    try:
        # Step 1: Extract NLP data (ingredient analysis)
        nlp_data = {}
        if product_data.get("ingredients_text"):
            logger.info(f"Calling NLP service with ingredients: {product_data.get('ingredients_text')[:100]}")
            try:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    nlp_response = await client.post(
                        f"{NLP_SERVICE}/nlp/extract",
                        json={"text": product_data["ingredients_text"]}
                    )
                    logger.info(f"NLP response status: {nlp_response.status_code}")
                    if nlp_response.status_code == 200:
                        nlp_data = nlp_response.json()
                        logger.info(f"NLP data received: {nlp_data}")
                    else:
                        logger.warning(f"NLP service returned {nlp_response.status_code}: {nlp_response.text}")
            except Exception as e:
                logger.error(f"NLP service error: {e}", exc_info=True)
        else:
            logger.warning("No ingredients_text provided, skipping NLP analysis")
        
        # Step 2: Calculate LCA impacts
        lca_data = {}
        if nlp_data.get("ingredients"):
            logger.info(f"Calling LCA service with {len(nlp_data['ingredients'])} ingredients")
            
            # Get product weight in kg (default to 1kg if not provided)
            product_weight_g = product_data.get("weight_g")
            if product_weight_g and product_weight_g > 0:
                product_weight_kg = product_weight_g / 1000.0
                logger.info(f"Using actual product weight: {product_weight_g}g = {product_weight_kg}kg")
            else:
                product_weight_kg = 1.0  # Default to 1kg if weight not available
                logger.info("Product weight not available, using default 1kg")
            
            # Smart weight distribution based on ingredient order (regulatory requirement: descending order)
            # First ingredients = higher percentage
            total_ingredients = len(nlp_data["ingredients"])
            ingredients_with_weights = []
            
            # Calculate weights using exponential decay for realistic distribution
            # First ingredient: ~30-40%, then decreasing rapidly
            raw_weights = []
            for idx in range(total_ingredients):
                # Exponential decay: weight = e^(-0.25 * position) for more aggressive distribution
                raw_weight = 2.71828 ** (-0.25 * idx)
                raw_weights.append(raw_weight)
            
            # Normalize to sum to product_weight_kg (actual product weight)
            total_raw = sum(raw_weights)
            normalized_weights = [(w / total_raw) * product_weight_kg for w in raw_weights]
            
            for idx, ingredient in enumerate(nlp_data["ingredients"]):
                # Use percentage if explicitly provided, otherwise use calculated weight
                if isinstance(ingredient, dict):
                    percentage = ingredient.get("percentage")
                    if percentage:
                        weight = (percentage / 100.0) * product_weight_kg  # Convert percentage to actual kg
                    else:
                        weight = normalized_weights[idx]  # Smart distribution based on actual weight
                    
                    ingredients_with_weights.append({
                        "name": ingredient.get("name", str(ingredient)),
                        "weight": weight,
                        "ecoinvent_id": ingredient.get("ecoinvent_id"),
                        "origin": product_data.get("origin")
                    })
                else:
                    # If ingredient is just a string
                    ingredients_with_weights.append({
                        "name": str(ingredient),
                        "weight": normalized_weights[idx],
                        "ecoinvent_id": None,
                        "origin": product_data.get("origin")
                    })
            
            logger.info(f"Ingredients with weights (total {product_weight_kg}kg): {ingredients_with_weights}")
            
            try:
                async with httpx.AsyncClient(timeout=180.0) as client:
                    lca_response = await client.post(
                        f"{LCA_SERVICE}/lca/calc",
                        json={
                            "ingredients": ingredients_with_weights,
                            "packaging_material": product_data.get("packaging", "plastic"),
                            "packaging_weight_kg": 0.05  # 50g default packaging
                        }
                    )
                    logger.info(f"LCA response status: {lca_response.status_code}")
                    if lca_response.status_code == 200:
                        lca_data = lca_response.json()
                        logger.info(f"LCA data received: {lca_data}")
                    else:
                        logger.warning(f"LCA service returned {lca_response.status_code}: {lca_response.text}")
            except Exception as e:
                logger.error(f"LCA service error: {e}", exc_info=True)
        else:
            logger.warning("No ingredients from NLP, skipping LCA calculation")
        
        # Fallback: Use local LCA calculation if no data from services
        if not lca_data and product_data.get("ingredients_text"):
            logger.info("Using local LCA calculation fallback")
            lca_data = calculate_local_lca(product_data["ingredients_text"])
            logger.info(f"Local LCA data: {lca_data}")
        
        # Get product weight for scoring
        product_weight_g = product_data.get("weight_g")
        product_weight_kg = (product_weight_g / 1000.0) if product_weight_g and product_weight_g > 0 else 1.0
        
        # Step 3: Calculate final eco-score
        score_data = {}
        if lca_data:
            logger.info(f"Calling Scoring service with product weight: {product_weight_kg}kg")
            try:
                async with httpx.AsyncClient(timeout=180.0) as client:
                    score_response = await client.post(
                        f"{SCORING_SERVICE}/score/compute",
                        json={
                            "indicators": {
                                "co2": lca_data.get("co2", 0),
                                "water": lca_data.get("water", 0),
                                "energy": lca_data.get("energy", 0),
                                "product_id": product_data.get("gtin", "")
                            },
                            "product_weight_kg": product_weight_kg
                        }
                    )
                    logger.info(f"Scoring response status: {score_response.status_code}")
                    if score_response.status_code == 200:
                        score_data = score_response.json()
                        logger.info(f"Score data received: {score_data}")
                    else:
                        logger.warning(f"Scoring service returned {score_response.status_code}: {score_response.text}")
            except Exception as e:
                logger.error(f"Scoring service error: {e}", exc_info=True)
        
        # Fallback: Use local score calculation if no data from services
        if not score_data and lca_data:
            logger.info("Using local score calculation fallback")
            score_data = calculate_local_score(
                lca_data.get("co2", 0),
                lca_data.get("water", 0),
                lca_data.get("energy", 0)
            )
            logger.info(f"Local score data: {score_data}")
        
        # Step 4: Save to database
        from models.product import ProductCreate
        
        product = create_or_update_product(
            db=db,
            product=ProductCreate(
                title=product_data.get("title", "Unknown Product"),
                brand=product_data.get("brand"),
                gtin=product_data.get("gtin"),
                ingredients=nlp_data.get("ingredients", []),
                origins=[product_data.get("origin")] if product_data.get("origin") else [],
                labels=[],
                score_letter=score_data.get("score_letter", "E"),
                score_numeric=score_data.get("score_numeric", 80),
                confidence=score_data.get("confidence", 0.5),
                co2=lca_data.get("co2", 0),
                water=lca_data.get("water", 0),
                energy=lca_data.get("energy", 0),
                weight_g=product_data.get("weight_g"),
                score_id=score_data.get("score_id")
            )
        )
        
        # Return full product with score
        return await get_product(str(product.id), db)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating product: {str(e)}"
        )


@router.get("/thresholds")
async def get_score_thresholds():
    """Get score thresholds for display"""
    return {
        "grades": [
            {"letter": "A", "label": "Excellent", "color": "#1E8449", "range": "0-20"},
            {"letter": "B", "label": "Good", "color": "#82E0AA", "range": "20-40"},
            {"letter": "C", "label": "Average", "color": "#F4D03F", "range": "40-60"},
            {"letter": "D", "label": "Poor", "color": "#E67E22", "range": "60-80"},
            {"letter": "E", "label": "Very Poor", "color": "#E74C3C", "range": "80-100"}
        ]
    }


@router.get("/widget/embed")
async def get_widget_embed_code(
    product_id: str,
    theme: str = "light"
):
    """Get embed code for widget"""
    api_url = os.getenv("PUBLIC_API_URL", "http://localhost:8005")
    
    embed_code = f'''
<div id="ecolabel-widget-{product_id}"></div>
<script src="{api_url}/widget.js"></script>
<script>
    EcoLabelWidget.init({{
        container: '#ecolabel-widget-{product_id}',
        productId: '{product_id}',
        theme: '{theme}',
        apiUrl: '{api_url}'
    }});
</script>
'''
    
    return {
        "product_id": product_id,
        "embed_code": embed_code,
        "cdn_url": f"{api_url}/widget.js"
    }


def get_score_color(letter: str) -> str:
    """Get color for score letter"""
    colors = {
        "A": "#1E8449",
        "B": "#82E0AA",
        "C": "#F4D03F",
        "D": "#E67E22",
        "E": "#E74C3C"
    }
    return colors.get(letter, "#808080")
