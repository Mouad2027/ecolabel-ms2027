"""
LCA Calculator
Computes environmental impacts for ingredients and packaging
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class LCACalculator:
    """
    Calculator for Life Cycle Assessment impacts
    Uses FAO, ADEME, and EcoInvent data
    """
    
    # Default impact factors (kg CO2e per kg ingredient)
    # Based on typical LCA databases
    DEFAULT_CO2_FACTORS = {
        # Cereals
        "wheat": 0.8,
        "rice": 2.7,
        "corn": 0.7,
        "oats": 0.6,
        "barley": 0.6,
        
        # Proteins
        "beef": 27.0,
        "pork": 5.8,
        "chicken": 3.7,
        "fish_generic": 3.5,
        "egg": 3.0,
        "milk": 1.3,
        "cheese": 8.5,
        
        # Vegetables
        "tomato": 1.1,
        "potato": 0.3,
        "onion": 0.3,
        "carrot": 0.3,
        "lettuce": 0.5,
        
        # Fruits
        "apple": 0.4,
        "orange": 0.4,
        "banana": 0.8,
        
        # Oils
        "palm_oil": 7.3,
        "sunflower_oil": 2.1,
        "olive_oil": 3.5,
        "coconut_oil": 2.3,
        "vegetable_oil_generic": 3.0,
        
        # Other
        "sugar": 0.6,
        "salt": 0.1,
        "water": 0.001,
        "cocoa": 4.5,
        "coffee": 6.0,
        "tea": 1.9,
        "soy": 0.4,
        "chocolate": 5.0,
        
        # Minerals (trace amounts in water - minimal impact)
        "sodium": 0.001,
        "calcium": 0.001,
        "magnesium": 0.001,
        "potassium": 0.001,
        "bicarbonates": 0.001,
        "sulfates": 0.001,
        "chlorides": 0.001,
        "chlorures": 0.001,
        "nitrates": 0.001,
        "fluorides": 0.001,
    }
    
    # Water consumption factors (liters per kg)
    DEFAULT_WATER_FACTORS = {
        "beef": 15400,
        "pork": 5988,
        "chicken": 4325,
        "egg": 3300,
        "milk": 1020,
        "cheese": 5060,
        "rice": 2497,
        "wheat": 1827,
        "corn": 1222,
        "sugar": 1782,
        "chocolate": 17196,
        "coffee": 15897,
        "tea": 8860,
        "apple": 822,
        "orange": 560,
        "banana": 790,
        "tomato": 214,
        "potato": 287,
        "olive_oil": 14430,
        "palm_oil": 5000,
        "sunflower_oil": 6800,
        "soy": 2145,
        "water": 1,
        "cocoa": 27000,
        "cocoa_bean": 27000,
        
        # Minerals (dissolved in water - no additional water needed)
        "sodium": 1,
        "calcium": 1,
        "magnesium": 1,
        "potassium": 1,
        "bicarbonates": 1,
        "sulfates": 1,
        "chlorides": 1,
        "chlorures": 1,
        "nitrates": 1,
        "fluorides": 1,
    }
    
    # Energy factors (MJ per kg)
    DEFAULT_ENERGY_FACTORS = {
        "beef": 35.0,
        "pork": 15.0,
        "chicken": 10.0,
        "milk": 2.5,
        "cheese": 12.0,
        "egg": 6.0,
        "wheat": 3.5,
        "rice": 5.0,
        "sugar": 5.5,
        "vegetable_oil_generic": 8.0,
        "chocolate": 15.0,
        "cocoa": 25.0,
        "cocoa_bean": 25.0,
        
        # Minerals (no processing energy - dissolved naturally)
        "sodium": 0.1,
        "calcium": 0.1,
        "magnesium": 0.1,
        "potassium": 0.1,
        "bicarbonates": 0.1,
        "sulfates": 0.1,
        "chlorides": 0.1,
        "chlorures": 0.1,
        "nitrates": 0.1,
        "fluorides": 0.1,
    }
    
    # Packaging impact factors
    PACKAGING_FACTORS = {
        "plastic": {"co2": 6.0, "water": 200, "energy": 80},
        "pet": {"co2": 5.5, "water": 180, "energy": 75},
        "hdpe": {"co2": 4.8, "water": 160, "energy": 70},
        "glass": {"co2": 1.2, "water": 30, "energy": 15},
        "aluminum": {"co2": 11.0, "water": 300, "energy": 170},
        "steel": {"co2": 2.8, "water": 80, "energy": 25},
        "cardboard": {"co2": 1.1, "water": 100, "energy": 12},
        "paper": {"co2": 1.3, "water": 150, "energy": 15},
        "wood": {"co2": 0.3, "water": 50, "energy": 5},
        "tetra_pak": {"co2": 1.5, "water": 120, "energy": 18},
    }
    
    def __init__(
        self, 
        ecoinvent_path: str = None,
        fao_path: str = None,
        ademe_path: str = None
    ):
        """
        Initialize LCA Calculator with dataset paths
        
        Args:
            ecoinvent_path: Path to EcoInvent dataset
            fao_path: Path to FAO dataset
            ademe_path: Path to ADEME dataset
        """
        self.ecoinvent_path = ecoinvent_path or os.getenv(
            "ECOINVENT_PATH", "/app/datasets/ecoinvent"
        )
        self.fao_path = fao_path or os.getenv(
            "FAO_PATH", "/app/datasets/fao"
        )
        self.ademe_path = ademe_path or os.getenv(
            "ADEME_PATH", "/app/datasets/ademe"
        )
        
        # Load factors from datasets
        self.co2_factors = self.DEFAULT_CO2_FACTORS.copy()
        self.water_factors = self.DEFAULT_WATER_FACTORS.copy()
        self.energy_factors = self.DEFAULT_ENERGY_FACTORS.copy()
        
        self._load_datasets()
    
    def _load_datasets(self):
        """Load impact factors from dataset files"""
        self._load_ecoinvent_data()
        self._load_fao_data()
        self._load_ademe_data()
    
    def _load_ecoinvent_data(self):
        """Load EcoInvent environmental factors"""
        factors_file = Path(self.ecoinvent_path) / "impact_factors.csv"
        
        if factors_file.exists() and PANDAS_AVAILABLE:
            try:
                df = pd.read_csv(factors_file)
                for _, row in df.iterrows():
                    ingredient = row.get("ingredient", "").lower()
                    if ingredient:
                        if "co2" in row:
                            self.co2_factors[ingredient] = float(row["co2"])
                        if "water" in row:
                            self.water_factors[ingredient] = float(row["water"])
                        if "energy" in row:
                            self.energy_factors[ingredient] = float(row["energy"])
            except Exception:
                # TODO: Add proper logging
                pass
    
    def _load_fao_data(self):
        """Load FAO agricultural impact coefficients"""
        factors_file = Path(self.fao_path) / "agricultural_factors.csv"
        
        if factors_file.exists() and PANDAS_AVAILABLE:
            try:
                df = pd.read_csv(factors_file)
                for _, row in df.iterrows():
                    ingredient = row.get("product", "").lower()
                    if ingredient and "water_footprint" in row:
                        self.water_factors[ingredient] = float(row["water_footprint"])
            except Exception:
                # TODO: Add proper logging
                pass
    
    def _load_ademe_data(self):
        """Load ADEME CO2 and transport factors"""
        factors_file = Path(self.ademe_path) / "co2_factors.json"
        
        if factors_file.exists():
            try:
                with open(factors_file, 'r') as f:
                    data = json.load(f)
                    if "ingredients" in data:
                        for ing, factor in data["ingredients"].items():
                            self.co2_factors[ing.lower()] = float(factor)
            except Exception:
                # TODO: Add proper logging
                pass
    
    def calculate_ingredient_impact(
        self,
        name: str,
        weight_kg: float,
        ecoinvent_id: Optional[str] = None,
        origin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate environmental impact for a single ingredient
        
        Args:
            name: Ingredient name
            weight_kg: Weight in kilograms
            ecoinvent_id: Optional EcoInvent database ID
            origin: Optional origin country
            
        Returns:
            Dictionary with CO2, water, and energy impacts
        """
        # Normalize name
        name_lower = name.lower().strip()
        
        # Get factors (use ecoinvent_id if available)
        lookup_key = ecoinvent_id.lower() if ecoinvent_id else name_lower
        
        co2_factor = self._get_factor(lookup_key, self.co2_factors, default=1.0)
        water_factor = self._get_factor(lookup_key, self.water_factors, default=500)
        energy_factor = self._get_factor(lookup_key, self.energy_factors, default=5.0)
        
        # Apply origin adjustment (simplified)
        origin_multiplier = self._get_origin_multiplier(origin)
        
        return {
            "name": name,
            "weight_kg": weight_kg,
            "co2": weight_kg * co2_factor * origin_multiplier,
            "water": weight_kg * water_factor,
            "energy": weight_kg * energy_factor,
            "factors_used": {
                "co2_factor": co2_factor,
                "water_factor": water_factor,
                "energy_factor": energy_factor,
                "origin_multiplier": origin_multiplier
            }
        }
    
    def calculate_packaging_impact(
        self,
        material: str,
        weight_kg: float
    ) -> Dict[str, float]:
        """
        Calculate environmental impact for packaging
        
        Args:
            material: Packaging material type
            weight_kg: Weight in kilograms
            
        Returns:
            Dictionary with CO2, water, and energy impacts
        """
        material_lower = material.lower().strip()
        
        # Get packaging factors
        factors = self.PACKAGING_FACTORS.get(
            material_lower, 
            {"co2": 3.0, "water": 100, "energy": 40}  # Default
        )
        
        return {
            "material": material,
            "weight_kg": weight_kg,
            "co2": weight_kg * factors["co2"],
            "water": weight_kg * factors["water"],
            "energy": weight_kg * factors["energy"]
        }
    
    def _get_factor(
        self, 
        key: str, 
        factors_dict: Dict, 
        default: float
    ) -> float:
        """
        Get factor from dictionary with fuzzy matching
        
        Args:
            key: Lookup key
            factors_dict: Dictionary of factors
            default: Default value if not found
            
        Returns:
            Factor value
        """
        # Direct lookup
        if key in factors_dict:
            return factors_dict[key]
        
        # Try partial matching
        for factor_key in factors_dict.keys():
            if key in factor_key or factor_key in key:
                return factors_dict[factor_key]
        
        return default
    
    def _get_origin_multiplier(self, origin: Optional[str]) -> float:
        """
        Get transport multiplier based on origin
        
        Args:
            origin: Origin country or region
            
        Returns:
            Multiplier for CO2 impact
        """
        if not origin:
            return 1.0
        
        origin_lower = origin.lower()
        
        # Simplified origin multipliers
        # Based on typical transport distances and modes
        long_distance = [
            "china", "india", "brazil", "argentina", "chile",
            "australia", "new zealand", "south africa", "indonesia"
        ]
        
        medium_distance = [
            "usa", "canada", "mexico", "morocco", "egypt",
            "turkey", "ukraine", "russia"
        ]
        
        for country in long_distance:
            if country in origin_lower:
                return 1.3
        
        for country in medium_distance:
            if country in origin_lower:
                return 1.15
        
        # European or local
        return 1.0
    
    def get_available_ingredients(self) -> List[str]:
        """Get list of ingredients with known impact factors"""
        return list(self.co2_factors.keys())
    
    def get_available_packaging_materials(self) -> List[str]:
        """Get list of packaging materials with known impact factors"""
        return list(self.PACKAGING_FACTORS.keys())
    
    def get_factor_info(self, ingredient: str) -> Dict[str, Any]:
        """
        Get factor information for an ingredient
        
        Args:
            ingredient: Ingredient name
            
        Returns:
            Dictionary with all available factors
        """
        name_lower = ingredient.lower()
        
        return {
            "ingredient": ingredient,
            "co2_factor": self.co2_factors.get(name_lower),
            "water_factor": self.water_factors.get(name_lower),
            "energy_factor": self.energy_factors.get(name_lower),
            "has_data": name_lower in self.co2_factors
        }
