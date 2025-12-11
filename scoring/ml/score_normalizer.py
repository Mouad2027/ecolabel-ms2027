"""
Score Normalizer
Normalizes LCA indicators using scikit-learn
"""

from typing import Dict, Any, List, Optional
import numpy as np

try:
    from sklearn.preprocessing import MinMaxScaler, StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ScoreNormalizer:
    """
    Normalizes LCA indicators to a common scale using scikit-learn
    """
    
    # Reference values for normalization (typical product ranges)
    # Based on average food product impacts per kg
    # STRICT THRESHOLDS - Only low-impact foods get good scores
    REFERENCE_RANGES = {
        "co2": {
            "min": 0.1,    # Very low impact (vegetables)
            "max": 3.0,    # Moderate impact (most processed foods should score poorly)
            "median": 1.5,
            "unit": "kg CO2e/kg"
        },
        "water": {
            "min": 100,     # Low water footprint
            "max": 1500,    # Moderate water footprint (strict threshold)
            "median": 800,
            "unit": "L/kg"
        },
        "energy": {
            "min": 1.0,    # Low energy
            "max": 8.0,    # Moderate energy (strict threshold)
            "median": 4.0,
            "unit": "MJ/kg"
        }
    }
    
    def __init__(self, use_sklearn: bool = True):
        """
        Initialize normalizer
        
        Args:
            use_sklearn: Whether to use scikit-learn for normalization
        """
        self.use_sklearn = use_sklearn and SKLEARN_AVAILABLE
        
        # Initialize scalers if sklearn is available
        if self.use_sklearn:
            self._init_scalers()
    
    def _init_scalers(self):
        """Initialize scikit-learn scalers with reference data"""
        # Create reference data for fitting scalers
        n_samples = 100
        
        # Generate synthetic reference data based on known ranges
        co2_data = np.linspace(
            self.REFERENCE_RANGES["co2"]["min"],
            self.REFERENCE_RANGES["co2"]["max"],
            n_samples
        ).reshape(-1, 1)
        
        water_data = np.linspace(
            self.REFERENCE_RANGES["water"]["min"],
            self.REFERENCE_RANGES["water"]["max"],
            n_samples
        ).reshape(-1, 1)
        
        energy_data = np.linspace(
            self.REFERENCE_RANGES["energy"]["min"],
            self.REFERENCE_RANGES["energy"]["max"],
            n_samples
        ).reshape(-1, 1)
        
        # Fit scalers
        self.co2_scaler = MinMaxScaler(feature_range=(0, 100))
        self.co2_scaler.fit(co2_data)
        
        self.water_scaler = MinMaxScaler(feature_range=(0, 100))
        self.water_scaler.fit(water_data)
        
        self.energy_scaler = MinMaxScaler(feature_range=(0, 100))
        self.energy_scaler.fit(energy_data)
    
    def normalize(
        self,
        co2: float,
        water: float,
        energy: float
    ) -> Dict[str, float]:
        """
        Normalize LCA indicators to 0-100 scale
        
        Args:
            co2: CO2 equivalent in kg
            water: Water consumption in liters
            energy: Energy consumption in MJ
            
        Returns:
            Dictionary with normalized values (0 = best, 100 = worst)
        """
        if self.use_sklearn:
            return self._normalize_sklearn(co2, water, energy)
        else:
            return self._normalize_manual(co2, water, energy)
    
    def _normalize_sklearn(
        self,
        co2: float,
        water: float,
        energy: float
    ) -> Dict[str, float]:
        """Normalize using scikit-learn scalers"""
        # Handle near-zero values (exceptional products like pure water)
        # If all impacts are negligible, assign excellent scores
        if co2 < 0.01 and water < 10 and energy < 0.5:
            return {
                "co2_normalized": 0.0,
                "water_normalized": 0.0,
                "energy_normalized": 0.0,
                "co2_raw": co2,
                "water_raw": water,
                "energy_raw": energy
            }
        
        # Transform values
        co2_normalized = self.co2_scaler.transform([[co2]])[0][0]
        water_normalized = self.water_scaler.transform([[water]])[0][0]
        energy_normalized = self.energy_scaler.transform([[energy]])[0][0]
        
        # Clip to 0-100 range
        co2_normalized = np.clip(co2_normalized, 0, 100)
        water_normalized = np.clip(water_normalized, 0, 100)
        energy_normalized = np.clip(energy_normalized, 0, 100)
        
        return {
            "co2_normalized": float(co2_normalized),
            "water_normalized": float(water_normalized),
            "energy_normalized": float(energy_normalized),
            "co2_raw": co2,
            "water_raw": water,
            "energy_raw": energy
        }
    
    def _normalize_manual(
        self,
        co2: float,
        water: float,
        energy: float
    ) -> Dict[str, float]:
        """Normalize using manual min-max scaling"""
        # Handle near-zero values (exceptional products like pure water)
        if co2 < 0.01 and water < 10 and energy < 0.5:
            return {
                "co2_normalized": 0.0,
                "water_normalized": 0.0,
                "energy_normalized": 0.0,
                "co2_raw": co2,
                "water_raw": water,
                "energy_raw": energy
            }
        
        def scale(value: float, min_val: float, max_val: float) -> float:
            if max_val == min_val:
                return 50.0
            scaled = (value - min_val) / (max_val - min_val) * 100
            return max(0, min(100, scaled))
        
        co2_normalized = scale(
            co2,
            self.REFERENCE_RANGES["co2"]["min"],
            self.REFERENCE_RANGES["co2"]["max"]
        )
        
        water_normalized = scale(
            water,
            self.REFERENCE_RANGES["water"]["min"],
            self.REFERENCE_RANGES["water"]["max"]
        )
        
        energy_normalized = scale(
            energy,
            self.REFERENCE_RANGES["energy"]["min"],
            self.REFERENCE_RANGES["energy"]["max"]
        )
        
        return {
            "co2_normalized": co2_normalized,
            "water_normalized": water_normalized,
            "energy_normalized": energy_normalized,
            "co2_raw": co2,
            "water_raw": water,
            "energy_raw": energy
        }
    
    def calculate_confidence(
        self,
        normalized_indicators: Dict[str, float]
    ) -> float:
        """
        Calculate confidence score based on how well values fit expected ranges
        
        Args:
            normalized_indicators: Normalized indicator values
            
        Returns:
            Confidence score (0-1)
        """
        scores = []
        
        # Check if values are within expected ranges
        for key in ["co2_normalized", "water_normalized", "energy_normalized"]:
            value = normalized_indicators.get(key, 50)
            
            # Values close to extremes reduce confidence
            if value < 5 or value > 95:
                scores.append(0.7)
            elif value < 10 or value > 90:
                scores.append(0.85)
            else:
                scores.append(1.0)
        
        return sum(scores) / len(scores)
    
    def get_percentile(
        self,
        indicator: str,
        value: float
    ) -> float:
        """
        Get percentile ranking for a value
        
        Args:
            indicator: Indicator name (co2, water, energy)
            value: Raw value
            
        Returns:
            Percentile (0-100)
        """
        if indicator not in self.REFERENCE_RANGES:
            return 50.0
        
        ref = self.REFERENCE_RANGES[indicator]
        
        if value <= ref["min"]:
            return 0.0
        if value >= ref["max"]:
            return 100.0
        
        # Simple linear interpolation
        return (value - ref["min"]) / (ref["max"] - ref["min"]) * 100
    
    def compare_to_median(
        self,
        indicator: str,
        value: float
    ) -> Dict[str, Any]:
        """
        Compare value to median reference
        
        Args:
            indicator: Indicator name
            value: Raw value
            
        Returns:
            Comparison result
        """
        if indicator not in self.REFERENCE_RANGES:
            return {"comparison": "unknown"}
        
        ref = self.REFERENCE_RANGES[indicator]
        median = ref["median"]
        
        ratio = value / median if median > 0 else 1.0
        
        if ratio < 0.5:
            comparison = "much_better"
        elif ratio < 0.8:
            comparison = "better"
        elif ratio < 1.2:
            comparison = "average"
        elif ratio < 2.0:
            comparison = "worse"
        else:
            comparison = "much_worse"
        
        return {
            "comparison": comparison,
            "ratio_to_median": round(ratio, 2),
            "median_value": median,
            "unit": ref["unit"]
        }
