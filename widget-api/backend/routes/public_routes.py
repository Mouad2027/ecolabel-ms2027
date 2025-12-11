"""
Public API routes for widget
"""

from fastapi import APIRouter, HTTPException, Depends, Query
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


@router.post("/products")
async def create_product_and_score(
    product_data: dict,
    db: Session = Depends(get_db)
):
    """
    Create/update product and calculate eco-score
    
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
                async with httpx.AsyncClient(timeout=90.0) as client:
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
            
            # Normalize to sum to 1.0
            total_raw = sum(raw_weights)
            normalized_weights = [w / total_raw for w in raw_weights]
            
            for idx, ingredient in enumerate(nlp_data["ingredients"]):
                # Use percentage if explicitly provided, otherwise use calculated weight
                if isinstance(ingredient, dict):
                    percentage = ingredient.get("percentage")
                    if percentage:
                        weight = percentage / 100.0  # Convert percentage to kg
                    else:
                        weight = normalized_weights[idx]  # Smart distribution
                    
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
            
            logger.info(f"Ingredients with weights: {ingredients_with_weights}")
            
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
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
        
        # Step 3: Calculate final eco-score
        score_data = {}
        if lca_data:
            logger.info("Calling Scoring service")
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    score_response = await client.post(
                        f"{SCORING_SERVICE}/score/compute",
                        json={
                            "indicators": {
                                "co2": lca_data.get("co2", 0),
                                "water": lca_data.get("water", 0),
                                "energy": lca_data.get("energy", 0),
                                "product_id": product_data.get("gtin", "")
                            },
                            "product_weight_kg": 1.0
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
        else:
            logger.warning("No LCA data, skipping score calculation")
        
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
