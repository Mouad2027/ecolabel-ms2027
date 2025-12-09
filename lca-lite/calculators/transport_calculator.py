"""
Transport Calculator
Computes environmental impacts for transportation
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class TransportCalculator:
    """
    Calculator for transport-related environmental impacts
    Uses ADEME transport factors
    """
    
    # Default transport emission factors (kg CO2 per ton-km)
    # Source: ADEME Base Carbone
    DEFAULT_TRANSPORT_FACTORS = {
        "truck": {
            "co2_per_tkm": 0.096,  # kg CO2 per ton-km
            "energy_per_tkm": 0.9  # MJ per ton-km
        },
        "truck_small": {
            "co2_per_tkm": 0.180,
            "energy_per_tkm": 1.5
        },
        "truck_large": {
            "co2_per_tkm": 0.050,
            "energy_per_tkm": 0.6
        },
        "ship": {
            "co2_per_tkm": 0.016,
            "energy_per_tkm": 0.2
        },
        "ship_container": {
            "co2_per_tkm": 0.010,
            "energy_per_tkm": 0.15
        },
        "train": {
            "co2_per_tkm": 0.022,
            "energy_per_tkm": 0.3
        },
        "train_freight": {
            "co2_per_tkm": 0.018,
            "energy_per_tkm": 0.25
        },
        "air": {
            "co2_per_tkm": 1.130,
            "energy_per_tkm": 15.0
        },
        "air_cargo": {
            "co2_per_tkm": 0.800,
            "energy_per_tkm": 12.0
        },
        "van": {
            "co2_per_tkm": 0.250,
            "energy_per_tkm": 2.5
        },
        "refrigerated_truck": {
            "co2_per_tkm": 0.150,
            "energy_per_tkm": 1.5
        }
    }
    
    # Average distances between regions (km)
    # Simplified for common trade routes
    REGIONAL_DISTANCES = {
        ("europe", "europe"): 500,
        ("europe", "asia"): 8000,
        ("europe", "north_america"): 6000,
        ("europe", "south_america"): 10000,
        ("europe", "africa"): 4000,
        ("europe", "oceania"): 15000,
        ("asia", "north_america"): 10000,
        ("asia", "south_america"): 15000,
    }
    
    def __init__(self, ademe_path: str = None):
        """
        Initialize Transport Calculator
        
        Args:
            ademe_path: Path to ADEME dataset
        """
        self.ademe_path = ademe_path or os.getenv(
            "ADEME_PATH", "/app/datasets/ademe"
        )
        
        self.transport_factors = self.DEFAULT_TRANSPORT_FACTORS.copy()
        self._load_ademe_transport_data()
    
    def _load_ademe_transport_data(self):
        """Load transport factors from ADEME dataset"""
        factors_file = Path(self.ademe_path) / "transport_factors.json"
        
        if factors_file.exists():
            try:
                with open(factors_file, 'r') as f:
                    data = json.load(f)
                    if "transport_modes" in data:
                        for mode, factors in data["transport_modes"].items():
                            self.transport_factors[mode.lower()] = factors
            except Exception:
                # TODO: Add proper logging
                pass
    
    def calculate_transport_impact(
        self,
        mode: str,
        distance_km: float,
        weight_kg: float
    ) -> Dict[str, float]:
        """
        Calculate environmental impact for transport
        
        Args:
            mode: Transport mode (truck, ship, train, air)
            distance_km: Distance in kilometers
            weight_kg: Weight of goods in kilograms
            
        Returns:
            Dictionary with CO2 and energy impacts
        """
        mode_lower = mode.lower().strip()
        
        # Get transport factors
        factors = self.transport_factors.get(
            mode_lower,
            self.DEFAULT_TRANSPORT_FACTORS.get("truck")  # Default to truck
        )
        
        # Convert weight to tons
        weight_tons = weight_kg / 1000.0
        
        # Calculate ton-kilometers
        ton_km = weight_tons * distance_km
        
        # Calculate impacts
        co2 = ton_km * factors["co2_per_tkm"]
        energy = ton_km * factors["energy_per_tkm"]
        
        return {
            "mode": mode,
            "distance_km": distance_km,
            "weight_kg": weight_kg,
            "ton_km": ton_km,
            "co2": co2,
            "energy": energy,
            "factors_used": {
                "co2_per_tkm": factors["co2_per_tkm"],
                "energy_per_tkm": factors["energy_per_tkm"]
            }
        }
    
    def calculate_multimodal_transport(
        self,
        segments: List[Dict[str, Any]],
        weight_kg: float
    ) -> Dict[str, float]:
        """
        Calculate impact for multimodal transport
        
        Args:
            segments: List of transport segments with mode and distance
            weight_kg: Total weight in kilograms
            
        Returns:
            Aggregated impacts
        """
        total_co2 = 0.0
        total_energy = 0.0
        segment_details = []
        
        for segment in segments:
            impact = self.calculate_transport_impact(
                mode=segment.get("mode", "truck"),
                distance_km=segment.get("distance_km", 0),
                weight_kg=segment.get("weight_kg", weight_kg)
            )
            total_co2 += impact["co2"]
            total_energy += impact["energy"]
            segment_details.append(impact)
        
        return {
            "total_co2": total_co2,
            "total_energy": total_energy,
            "segments": segment_details
        }
    
    def estimate_distance(
        self,
        origin_region: str,
        destination_region: str
    ) -> float:
        """
        Estimate distance between regions
        
        Args:
            origin_region: Origin region name
            destination_region: Destination region name
            
        Returns:
            Estimated distance in kilometers
        """
        origin = origin_region.lower()
        dest = destination_region.lower()
        
        # Try direct lookup
        key = (origin, dest)
        if key in self.REGIONAL_DISTANCES:
            return self.REGIONAL_DISTANCES[key]
        
        # Try reverse
        key_reverse = (dest, origin)
        if key_reverse in self.REGIONAL_DISTANCES:
            return self.REGIONAL_DISTANCES[key_reverse]
        
        # Default distance
        return 1000  # Default 1000 km
    
    def get_available_modes(self) -> List[str]:
        """Get list of available transport modes"""
        return list(self.transport_factors.keys())
    
    def get_mode_factors(self, mode: str) -> Dict[str, float]:
        """
        Get emission factors for a transport mode
        
        Args:
            mode: Transport mode
            
        Returns:
            Dictionary with CO2 and energy factors
        """
        mode_lower = mode.lower()
        return self.transport_factors.get(mode_lower, {})
    
    def compare_modes(
        self,
        distance_km: float,
        weight_kg: float
    ) -> List[Dict[str, Any]]:
        """
        Compare impacts across all transport modes
        
        Args:
            distance_km: Distance in kilometers
            weight_kg: Weight in kilograms
            
        Returns:
            List of impacts for each mode, sorted by CO2
        """
        results = []
        
        for mode in self.transport_factors.keys():
            impact = self.calculate_transport_impact(mode, distance_km, weight_kg)
            results.append({
                "mode": mode,
                "co2": impact["co2"],
                "energy": impact["energy"]
            })
        
        # Sort by CO2 impact
        return sorted(results, key=lambda x: x["co2"])
