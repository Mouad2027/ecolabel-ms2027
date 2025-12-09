"""
Ingredient Mapper
Maps extracted ingredients to EcoInvent taxonomy
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class IngredientMapper:
    """
    Maps ingredient names to EcoInvent database entries
    """
    
    # Default ingredient mappings (fallback when dataset not available)
    DEFAULT_MAPPINGS = {
        # Common food ingredients
        "water": {"ecoinvent_id": "tap_water", "category": "beverage", "unit": "kg"},
        "sugar": {"ecoinvent_id": "sugar_beet", "category": "sweetener", "unit": "kg"},
        "salt": {"ecoinvent_id": "sodium_chloride", "category": "mineral", "unit": "kg"},
        "wheat": {"ecoinvent_id": "wheat_grain", "category": "cereal", "unit": "kg"},
        "flour": {"ecoinvent_id": "wheat_flour", "category": "cereal", "unit": "kg"},
        "rice": {"ecoinvent_id": "rice_grain", "category": "cereal", "unit": "kg"},
        "corn": {"ecoinvent_id": "corn_grain", "category": "cereal", "unit": "kg"},
        "milk": {"ecoinvent_id": "raw_milk", "category": "dairy", "unit": "kg"},
        "butter": {"ecoinvent_id": "butter", "category": "dairy", "unit": "kg"},
        "cream": {"ecoinvent_id": "cream", "category": "dairy", "unit": "kg"},
        "cheese": {"ecoinvent_id": "cheese", "category": "dairy", "unit": "kg"},
        "egg": {"ecoinvent_id": "egg", "category": "animal", "unit": "kg"},
        "eggs": {"ecoinvent_id": "egg", "category": "animal", "unit": "kg"},
        "chicken": {"ecoinvent_id": "chicken_meat", "category": "meat", "unit": "kg"},
        "beef": {"ecoinvent_id": "beef_meat", "category": "meat", "unit": "kg"},
        "pork": {"ecoinvent_id": "pork_meat", "category": "meat", "unit": "kg"},
        "fish": {"ecoinvent_id": "fish_generic", "category": "seafood", "unit": "kg"},
        "soy": {"ecoinvent_id": "soybean", "category": "legume", "unit": "kg"},
        "soybean": {"ecoinvent_id": "soybean", "category": "legume", "unit": "kg"},
        "palm oil": {"ecoinvent_id": "palm_oil", "category": "oil", "unit": "kg"},
        "sunflower oil": {"ecoinvent_id": "sunflower_oil", "category": "oil", "unit": "kg"},
        "olive oil": {"ecoinvent_id": "olive_oil", "category": "oil", "unit": "kg"},
        "coconut oil": {"ecoinvent_id": "coconut_oil", "category": "oil", "unit": "kg"},
        "vegetable oil": {"ecoinvent_id": "vegetable_oil_generic", "category": "oil", "unit": "kg"},
        "tomato": {"ecoinvent_id": "tomato", "category": "vegetable", "unit": "kg"},
        "potato": {"ecoinvent_id": "potato", "category": "vegetable", "unit": "kg"},
        "onion": {"ecoinvent_id": "onion", "category": "vegetable", "unit": "kg"},
        "carrot": {"ecoinvent_id": "carrot", "category": "vegetable", "unit": "kg"},
        "apple": {"ecoinvent_id": "apple", "category": "fruit", "unit": "kg"},
        "orange": {"ecoinvent_id": "orange", "category": "fruit", "unit": "kg"},
        "banana": {"ecoinvent_id": "banana", "category": "fruit", "unit": "kg"},
        "cocoa": {"ecoinvent_id": "cocoa_bean", "category": "tropical", "unit": "kg"},
        "chocolate": {"ecoinvent_id": "chocolate", "category": "processed", "unit": "kg"},
        "coffee": {"ecoinvent_id": "coffee_bean", "category": "tropical", "unit": "kg"},
        "tea": {"ecoinvent_id": "tea_leaf", "category": "tropical", "unit": "kg"},
        "vanilla": {"ecoinvent_id": "vanilla", "category": "spice", "unit": "kg"},
        "cinnamon": {"ecoinvent_id": "cinnamon", "category": "spice", "unit": "kg"},
        "pepper": {"ecoinvent_id": "pepper", "category": "spice", "unit": "kg"},
    }
    
    # Synonym mappings
    SYNONYMS = {
        "sucre": "sugar",
        "azúcar": "sugar",
        "zucker": "sugar",
        "eau": "water",
        "agua": "water",
        "wasser": "water",
        "sel": "salt",
        "sal": "salt",
        "salz": "salt",
        "farine": "flour",
        "harina": "flour",
        "mehl": "flour",
        "lait": "milk",
        "leche": "milk",
        "milch": "milk",
        "beurre": "butter",
        "mantequilla": "butter",
        "œuf": "egg",
        "oeuf": "egg",
        "huevo": "egg",
        "ei": "egg",
        "poulet": "chicken",
        "pollo": "chicken",
        "hähnchen": "chicken",
        "bœuf": "beef",
        "boeuf": "beef",
        "ternera": "beef",
        "rindfleisch": "beef",
        "porc": "pork",
        "cerdo": "pork",
        "schweinefleisch": "pork",
        "poisson": "fish",
        "pescado": "fish",
        "fisch": "fish",
        "huile de palme": "palm oil",
        "aceite de palma": "palm oil",
        "huile de tournesol": "sunflower oil",
        "huile d'olive": "olive oil",
    }
    
    def __init__(self, ecoinvent_path: Optional[str] = None):
        """
        Initialize IngredientMapper
        
        Args:
            ecoinvent_path: Path to EcoInvent dataset directory
        """
        self.ecoinvent_path = ecoinvent_path or os.getenv(
            "ECOINVENT_PATH",
            "/app/datasets/ecoinvent"
        )
        self.mappings = self.DEFAULT_MAPPINGS.copy()
        self._load_ecoinvent_data()
    
    def _load_ecoinvent_data(self):
        """Load EcoInvent mappings from dataset"""
        mappings_file = Path(self.ecoinvent_path) / "ingredient_mappings.json"
        
        if mappings_file.exists():
            try:
                with open(mappings_file, 'r', encoding='utf-8') as f:
                    ecoinvent_data = json.load(f)
                    self.mappings.update(ecoinvent_data)
            except Exception:
                # TODO: Add proper logging
                pass
    
    def map_to_ecoinvent(
        self, 
        ingredients: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Map ingredient names to EcoInvent entries
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            List of mapped ingredients with EcoInvent data
        """
        mapped = []
        
        for ingredient in ingredients:
            mapped_data = self.map_single_ingredient(ingredient)
            mapped.append(mapped_data)
        
        return mapped
    
    def map_single_ingredient(self, ingredient: str) -> Dict[str, Any]:
        """
        Map a single ingredient to EcoInvent
        
        Args:
            ingredient: Ingredient name
            
        Returns:
            Mapped ingredient data
        """
        # Handle dict input from parsed ingredients
        if isinstance(ingredient, dict):
            name = ingredient.get("name", "")
            percentage = ingredient.get("percentage")
        else:
            name = str(ingredient)
            percentage = None
        
        # Normalize name
        normalized = self._normalize_name(name)
        
        # Check direct mapping
        if normalized in self.mappings:
            mapping = self.mappings[normalized].copy()
            return {
                "name": name,
                "normalized_name": normalized,
                "percentage": percentage,
                "ecoinvent_id": mapping.get("ecoinvent_id"),
                "category": mapping.get("category"),
                "unit": mapping.get("unit", "kg"),
                "mapped": True
            }
        
        # Check synonyms
        if normalized in self.SYNONYMS:
            canonical = self.SYNONYMS[normalized]
            if canonical in self.mappings:
                mapping = self.mappings[canonical].copy()
                return {
                    "name": name,
                    "normalized_name": canonical,
                    "percentage": percentage,
                    "ecoinvent_id": mapping.get("ecoinvent_id"),
                    "category": mapping.get("category"),
                    "unit": mapping.get("unit", "kg"),
                    "mapped": True
                }
        
        # Try fuzzy matching
        fuzzy_match = self._fuzzy_match(normalized)
        if fuzzy_match:
            mapping = self.mappings[fuzzy_match].copy()
            return {
                "name": name,
                "normalized_name": fuzzy_match,
                "percentage": percentage,
                "ecoinvent_id": mapping.get("ecoinvent_id"),
                "category": mapping.get("category"),
                "unit": mapping.get("unit", "kg"),
                "mapped": True,
                "fuzzy_matched": True
            }
        
        # No mapping found
        return {
            "name": name,
            "normalized_name": normalized,
            "percentage": percentage,
            "ecoinvent_id": None,
            "category": "unknown",
            "unit": "kg",
            "mapped": False
        }
    
    def _normalize_name(self, name: str) -> str:
        """Normalize ingredient name for matching"""
        import re
        
        # Lowercase
        normalized = name.lower().strip()
        
        # Remove common suffixes
        normalized = re.sub(r'\s*\(.*\)$', '', normalized)
        normalized = re.sub(r'\s*\[.*\]$', '', normalized)
        
        # Remove percentages
        normalized = re.sub(r'\d+(\.\d+)?%', '', normalized)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove special characters
        normalized = re.sub(r'[*†‡™®]', '', normalized)
        
        return normalized
    
    def _fuzzy_match(self, name: str, threshold: float = 0.8) -> Optional[str]:
        """
        Find fuzzy match in mappings
        
        Args:
            name: Normalized ingredient name
            threshold: Minimum similarity score
            
        Returns:
            Best matching key or None
        """
        best_match = None
        best_score = 0
        
        for key in self.mappings.keys():
            score = self._similarity_score(name, key)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = key
        
        return best_match
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """Calculate simple similarity score between two strings"""
        if not s1 or not s2:
            return 0.0
        
        # Check if one contains the other
        if s1 in s2 or s2 in s1:
            return 0.9
        
        # Simple Jaccard similarity on words
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def get_category(self, ingredient_name: str) -> str:
        """Get category for an ingredient"""
        mapped = self.map_single_ingredient(ingredient_name)
        return mapped.get("category", "unknown")
    
    def get_ecoinvent_id(self, ingredient_name: str) -> Optional[str]:
        """Get EcoInvent ID for an ingredient"""
        mapped = self.map_single_ingredient(ingredient_name)
        return mapped.get("ecoinvent_id")
    
    def add_mapping(self, name: str, ecoinvent_id: str, category: str, unit: str = "kg"):
        """
        Add a new ingredient mapping
        
        Args:
            name: Ingredient name
            ecoinvent_id: EcoInvent database ID
            category: Ingredient category
            unit: Unit of measurement
        """
        self.mappings[name.lower()] = {
            "ecoinvent_id": ecoinvent_id,
            "category": category,
            "unit": unit
        }
