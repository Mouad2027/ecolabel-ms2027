"""
Score Calculator
Calculates weighted eco-score and converts to letter grades
"""

from typing import Dict, Any, List, Optional


class ScoreCalculator:
    """
    Calculator for eco-score from normalized LCA indicators
    """
    
    # Default weights for indicators (should sum to 1.0)
    DEFAULT_WEIGHTS = {
        "co2": 0.50,      # Climate change is weighted highest
        "water": 0.30,    # Water scarcity
        "energy": 0.20    # Energy consumption
    }
    
    # Score thresholds for letter grades
    # Lower score = better (0 = best, 100 = worst)
    GRADE_THRESHOLDS = {
        "A": (0, 20),      # Excellent
        "B": (20, 40),     # Good
        "C": (40, 60),     # Average
        "D": (60, 80),     # Poor
        "E": (80, 100)     # Very poor
    }
    
    # Bonus/malus adjustments (points)
    ADJUSTMENTS = {
        # Bonuses (reduce score = improve grade)
        "bio_certified": -10,
        "recyclable_packaging": -5,
        "local_sourcing": -8,
        "fair_trade": -3,
        
        # Malus (increase score = worsen grade)
        "endangered_species": +15,
        "deforestation_risk": +12,
        "excessive_packaging": +5,
        "long_distance_transport": +7
    }
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize calculator with optional custom weights
        
        Args:
            weights: Custom weights for indicators
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        
        # Ensure weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            for key in self.weights:
                self.weights[key] /= total
    
    def calculate_weighted_score(
        self,
        normalized_co2: float,
        normalized_water: float,
        normalized_energy: float
    ) -> float:
        """
        Calculate weighted score from normalized indicators
        
        Args:
            normalized_co2: Normalized CO2 score (0-100)
            normalized_water: Normalized water score (0-100)
            normalized_energy: Normalized energy score (0-100)
            
        Returns:
            Weighted score (0-100, lower is better)
        """
        score = (
            normalized_co2 * self.weights["co2"] +
            normalized_water * self.weights["water"] +
            normalized_energy * self.weights["energy"]
        )
        
        return max(0, min(100, score))
    
    def apply_bonus_malus(
        self,
        base_score: float,
        bio_certified: bool = False,
        recyclable_packaging: bool = False,
        local_sourcing: bool = False,
        fair_trade: bool = False,
        endangered_species: bool = False,
        deforestation_risk: bool = False
    ) -> Dict[str, Any]:
        """
        Apply bonus and malus adjustments to base score
        
        Args:
            base_score: Base weighted score
            bio_certified: Product is bio/organic certified
            recyclable_packaging: Packaging is recyclable
            local_sourcing: Ingredients are locally sourced
            fair_trade: Product has fair trade certification
            endangered_species: Product uses endangered species
            deforestation_risk: Production linked to deforestation
            
        Returns:
            Dictionary with adjusted score and adjustment details
        """
        adjustments = []
        total_adjustment = 0
        
        if bio_certified:
            adj = self.ADJUSTMENTS["bio_certified"]
            total_adjustment += adj
            adjustments.append({
                "type": "bio_certified",
                "label": "Organic Certification",
                "points": adj
            })
        
        if recyclable_packaging:
            adj = self.ADJUSTMENTS["recyclable_packaging"]
            total_adjustment += adj
            adjustments.append({
                "type": "recyclable_packaging",
                "label": "Recyclable Packaging",
                "points": adj
            })
        
        if local_sourcing:
            adj = self.ADJUSTMENTS["local_sourcing"]
            total_adjustment += adj
            adjustments.append({
                "type": "local_sourcing",
                "label": "Local Sourcing",
                "points": adj
            })
        
        if fair_trade:
            adj = self.ADJUSTMENTS["fair_trade"]
            total_adjustment += adj
            adjustments.append({
                "type": "fair_trade",
                "label": "Fair Trade Certified",
                "points": adj
            })
        
        if endangered_species:
            adj = self.ADJUSTMENTS["endangered_species"]
            total_adjustment += adj
            adjustments.append({
                "type": "endangered_species",
                "label": "Endangered Species Risk",
                "points": adj
            })
        
        if deforestation_risk:
            adj = self.ADJUSTMENTS["deforestation_risk"]
            total_adjustment += adj
            adjustments.append({
                "type": "deforestation_risk",
                "label": "Deforestation Risk",
                "points": adj
            })
        
        adjusted_score = max(0, min(100, base_score + total_adjustment))
        
        return {
            "base_score": base_score,
            "total_adjustment": total_adjustment,
            "adjusted_score": adjusted_score,
            "adjustments": adjustments
        }
    
    def numeric_to_letter(self, score: float) -> str:
        """
        Convert numeric score to letter grade
        
        Args:
            score: Numeric score (0-100)
            
        Returns:
            Letter grade (A-E)
        """
        for letter, (min_val, max_val) in self.GRADE_THRESHOLDS.items():
            if min_val <= score < max_val:
                return letter
        
        # Edge cases
        if score < 0:
            return "A"
        return "E"
    
    def letter_to_numeric_range(self, letter: str) -> tuple:
        """
        Get numeric range for a letter grade
        
        Args:
            letter: Letter grade (A-E)
            
        Returns:
            Tuple of (min, max) scores
        """
        return self.GRADE_THRESHOLDS.get(letter.upper(), (0, 100))
    
    def generate_explanation(
        self,
        score: float,
        letter: str,
        normalized_indicators: Dict[str, float],
        adjustments: List[Dict] = None
    ) -> str:
        """
        Generate human-readable explanation for the score
        
        Args:
            score: Numeric score
            letter: Letter grade
            normalized_indicators: Normalized indicator values
            adjustments: Applied adjustments
            
        Returns:
            Explanation string
        """
        explanations = {
            "A": "This product has excellent environmental performance with very low impacts across all indicators.",
            "B": "This product has good environmental performance with low impacts.",
            "C": "This product has average environmental performance. There is room for improvement.",
            "D": "This product has below average environmental performance with notable impacts.",
            "E": "This product has poor environmental performance with high environmental impacts."
        }
        
        base_explanation = explanations.get(letter, "Environmental score calculated.")
        
        # Add indicator insights
        insights = []
        
        co2_norm = normalized_indicators.get("co2_normalized", 50)
        water_norm = normalized_indicators.get("water_normalized", 50)
        energy_norm = normalized_indicators.get("energy_normalized", 50)
        
        if co2_norm < 30:
            insights.append("Low carbon footprint")
        elif co2_norm > 70:
            insights.append("High carbon footprint")
        
        if water_norm < 30:
            insights.append("Low water usage")
        elif water_norm > 70:
            insights.append("High water usage")
        
        if energy_norm < 30:
            insights.append("Low energy consumption")
        elif energy_norm > 70:
            insights.append("High energy consumption")
        
        # Add adjustment info
        if adjustments:
            bonuses = [a["label"] for a in adjustments if a["points"] < 0]
            penalties = [a["label"] for a in adjustments if a["points"] > 0]
            
            if bonuses:
                insights.append(f"Bonuses: {', '.join(bonuses)}")
            if penalties:
                insights.append(f"Concerns: {', '.join(penalties)}")
        
        if insights:
            return f"{base_explanation} Key factors: {'; '.join(insights)}."
        
        return base_explanation
    
    def get_weights(self) -> Dict[str, float]:
        """Get current indicator weights"""
        return self.weights.copy()
    
    def get_thresholds(self) -> Dict[str, tuple]:
        """Get grade thresholds"""
        return self.GRADE_THRESHOLDS.copy()
    
    def get_grade_color(self, letter: str) -> str:
        """
        Get display color for grade
        
        Args:
            letter: Letter grade
            
        Returns:
            Hex color code
        """
        colors = {
            "A": "#1E8449",  # Dark green
            "B": "#82E0AA",  # Light green
            "C": "#F4D03F",  # Yellow
            "D": "#E67E22",  # Orange
            "E": "#E74C3C"   # Red
        }
        return colors.get(letter.upper(), "#808080")
    
    def simulate_improvements(
        self,
        current_score: float,
        improvements: List[str]
    ) -> Dict[str, Any]:
        """
        Simulate score improvements
        
        Args:
            current_score: Current score
            improvements: List of improvement types
            
        Returns:
            Simulation results
        """
        potential_savings = 0
        improvement_details = []
        
        for improvement in improvements:
            if improvement in self.ADJUSTMENTS:
                saving = abs(self.ADJUSTMENTS[improvement])
                potential_savings += saving
                improvement_details.append({
                    "improvement": improvement,
                    "potential_points": saving
                })
        
        new_score = max(0, current_score - potential_savings)
        current_grade = self.numeric_to_letter(current_score)
        new_grade = self.numeric_to_letter(new_score)
        
        return {
            "current_score": current_score,
            "current_grade": current_grade,
            "potential_score": new_score,
            "potential_grade": new_grade,
            "potential_improvement": potential_savings,
            "grade_change": current_grade != new_grade,
            "details": improvement_details
        }
