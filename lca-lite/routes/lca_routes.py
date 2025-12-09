"""
API routes for LCA calculations
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import uuid

from calculators.lca_calculator import LCACalculator
from calculators.transport_calculator import TransportCalculator
from database.connection import get_db
from database.crud import create_lca_result, get_lca_result
from models.lca import LCAResultCreate
from utils.minio_client import MinioStorage

router = APIRouter()

# Initialize calculators
lca_calculator = LCACalculator()
transport_calculator = TransportCalculator()
minio_storage = MinioStorage()


class IngredientInput(BaseModel):
    """Input model for a single ingredient"""
    name: str
    weight: float  # in kg
    ecoinvent_id: Optional[str] = None
    origin: Optional[str] = None


class TransportInput(BaseModel):
    """Input model for transport information"""
    mode: str  # truck, ship, train, air
    distance_km: float
    weight_kg: Optional[float] = None


class LCARequest(BaseModel):
    """Request model for LCA calculation"""
    product_id: Optional[str] = None
    ingredients: List[IngredientInput]
    transport: Optional[List[TransportInput]] = None
    packaging_material: Optional[str] = None
    packaging_weight_kg: Optional[float] = None


class LCAResponse(BaseModel):
    """Response model for LCA calculation"""
    id: Optional[str] = None
    co2: float  # kg CO2 equivalent
    water: float  # liters
    energy: float  # MJ
    breakdown: Optional[dict] = None


@router.post("/calc", response_model=LCAResponse)
async def calculate_lca(
    request: LCARequest,
    db: Session = Depends(get_db)
):
    """
    Calculate simplified LCA indicators
    
    Input: ingredients + transport info
    Output: CO2, water, energy metrics
    """
    try:
        # Calculate ingredient impacts
        ingredient_impacts = []
        for ingredient in request.ingredients:
            impact = lca_calculator.calculate_ingredient_impact(
                name=ingredient.name,
                weight_kg=ingredient.weight,
                ecoinvent_id=ingredient.ecoinvent_id,
                origin=ingredient.origin
            )
            ingredient_impacts.append(impact)
        
        # Aggregate ingredient impacts
        total_co2 = sum(i["co2"] for i in ingredient_impacts)
        total_water = sum(i["water"] for i in ingredient_impacts)
        total_energy = sum(i["energy"] for i in ingredient_impacts)
        
        # Calculate transport impacts
        transport_co2 = 0.0
        transport_energy = 0.0
        
        if request.transport:
            total_weight = sum(i.weight for i in request.ingredients)
            for transport in request.transport:
                t_impact = transport_calculator.calculate_transport_impact(
                    mode=transport.mode,
                    distance_km=transport.distance_km,
                    weight_kg=transport.weight_kg or total_weight
                )
                transport_co2 += t_impact["co2"]
                transport_energy += t_impact["energy"]
        
        # Calculate packaging impacts
        packaging_co2 = 0.0
        packaging_water = 0.0
        packaging_energy = 0.0
        
        if request.packaging_material and request.packaging_weight_kg:
            p_impact = lca_calculator.calculate_packaging_impact(
                material=request.packaging_material,
                weight_kg=request.packaging_weight_kg
            )
            packaging_co2 = p_impact["co2"]
            packaging_water = p_impact["water"]
            packaging_energy = p_impact["energy"]
        
        # Total impacts
        result = {
            "co2": round(total_co2 + transport_co2 + packaging_co2, 4),
            "water": round(total_water + packaging_water, 4),
            "energy": round(total_energy + transport_energy + packaging_energy, 4),
            "breakdown": {
                "ingredients": {
                    "co2": round(total_co2, 4),
                    "water": round(total_water, 4),
                    "energy": round(total_energy, 4),
                    "details": ingredient_impacts
                },
                "transport": {
                    "co2": round(transport_co2, 4),
                    "energy": round(transport_energy, 4)
                },
                "packaging": {
                    "co2": round(packaging_co2, 4),
                    "water": round(packaging_water, 4),
                    "energy": round(packaging_energy, 4)
                }
            }
        }
        
        # Store result in database
        lca_data = LCAResultCreate(
            product_id=request.product_id,
            co2=result["co2"],
            water=result["water"],
            energy=result["energy"],
            breakdown=result["breakdown"]
        )
        
        db_result = create_lca_result(db, lca_data)
        result["id"] = str(db_result.id)
        
        # Store raw calculation in MinIO
        try:
            minio_storage.store_calculation(
                calculation_id=str(db_result.id),
                data={
                    "request": request.dict(),
                    "result": result
                }
            )
        except Exception:
            # TODO: Add proper logging
            pass
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LCA calculation error: {str(e)}")


@router.get("/result/{lca_id}")
async def get_lca_result_by_id(
    lca_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a previous LCA calculation result by ID"""
    try:
        lca_uuid = uuid.UUID(lca_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid LCA result ID format")
    
    result = get_lca_result(db, lca_uuid)
    if not result:
        raise HTTPException(status_code=404, detail="LCA result not found")
    
    return {
        "id": str(result.id),
        "product_id": result.product_id,
        "co2": result.co2,
        "water": result.water,
        "energy": result.energy,
        "breakdown": result.breakdown,
        "created_at": result.created_at.isoformat()
    }


@router.get("/factors")
async def get_available_factors():
    """Get list of available impact factors"""
    return {
        "ingredients": lca_calculator.get_available_ingredients(),
        "transport_modes": transport_calculator.get_available_modes(),
        "packaging_materials": lca_calculator.get_available_packaging_materials()
    }
