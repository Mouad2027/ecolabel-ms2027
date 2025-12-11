"""
spaCy Pipeline for entity extraction
"""

import re
from typing import Dict, List, Any, Optional

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class SpacyPipeline:
    """
    spaCy-based NLP pipeline for extracting entities from product text
    """
    
    # Supported languages and their models
    LANGUAGE_MODELS = {
        "en": "en_core_web_sm",
        "fr": "fr_core_news_sm",
        "de": "de_core_news_sm",
        "es": "es_core_news_sm",
        "it": "it_core_news_sm",
        "multi": "xx_ent_wiki_sm"
    }
    
    # Ingredient-related patterns
    INGREDIENT_PATTERNS = [
        r'(?:ingredients?|composition|ingrédients?)\s*[:\-]?\s*(.+?)(?=\.|$|\n\n)',
    ]
    
    # Common label keywords
    LABEL_KEYWORDS = {
        "bio": ["bio", "organic", "biologique", "ökologisch", "ecológico"],
        "recyclable": ["recyclable", "recycled", "recyclé", "recycle"],
        "vegan": ["vegan", "végétalien", "vegano"],
        "fair_trade": ["fair trade", "fairtrade", "commerce équitable"],
        "non_gmo": ["non-gmo", "sans ogm", "gmo-free"],
        "gluten_free": ["gluten-free", "sans gluten", "glutenfrei"],
        "natural": ["natural", "naturel", "natürlich", "100% natural"]
    }
    
    # Packaging material keywords
    MATERIAL_KEYWORDS = [
        "plastic", "plastique", "glass", "verre", "metal", "métal",
        "aluminum", "aluminium", "cardboard", "carton", "paper", "papier",
        "wood", "bois", "tin", "steel", "acier", "pet", "hdpe", "ldpe",
        "pp", "ps", "pvc", "tetra pak", "biodegradable"
    ]
    
    def __init__(self):
        """Initialize spaCy pipeline"""
        self.nlp_models = {}
        self._load_default_model()
    
    def _load_default_model(self):
        """Load default English model"""
        if not SPACY_AVAILABLE:
            return
        
        try:
            self.nlp_models["en"] = spacy.load("en_core_web_sm")
        except OSError:
            # Model not installed, try to download
            try:
                spacy.cli.download("en_core_web_sm")
                self.nlp_models["en"] = spacy.load("en_core_web_sm")
            except Exception:
                # TODO: Add proper logging
                pass
    
    def _get_model(self, language: str):
        """Get or load spaCy model for language"""
        if not SPACY_AVAILABLE:
            return None
        
        if language in self.nlp_models:
            return self.nlp_models[language]
        
        model_name = self.LANGUAGE_MODELS.get(language, "en_core_web_sm")
        
        try:
            self.nlp_models[language] = spacy.load(model_name)
            return self.nlp_models[language]
        except OSError:
            # Fall back to English or multilingual
            if "en" in self.nlp_models:
                return self.nlp_models["en"]
            return None
    
    def extract_entities(
        self, 
        text: str, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Extract entities from text using spaCy
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            Dictionary with extracted entities
        """
        result = {
            "ingredients": [],
            "materials": [],
            "origins": [],
            "labels": [],
            "entities": []
        }
        
        if not text:
            return result
        
        # Use spaCy NER if available
        if SPACY_AVAILABLE:
            nlp = self._get_model(language)
            if nlp:
                result = self._spacy_extraction(text, nlp)
        
        # Supplement with regex-based extraction
        regex_results = self._regex_extraction(text)
        
        # Merge results
        result["ingredients"] = list(set(result["ingredients"] + regex_results["ingredients"]))
        result["materials"] = list(set(result["materials"] + regex_results["materials"]))
        result["labels"] = list(set(result["labels"] + regex_results["labels"]))
        
        # If no ingredients found, treat entire text as ingredient list
        if not result["ingredients"]:
            # Split by common delimiters
            parts = re.split(r'[,;•\n]', text)
            result["ingredients"] = [
                part.strip() for part in parts 
                if part.strip() and len(part.strip()) > 2
            ]
        
        return result
    
    def _spacy_extraction(self, text: str, nlp) -> Dict[str, Any]:
        """
        Extract entities using spaCy NER
        
        Args:
            text: Input text
            nlp: spaCy model
            
        Returns:
            Dictionary with extracted entities
        """
        doc = nlp(text)
        
        result = {
            "ingredients": [],
            "materials": [],
            "origins": [],
            "labels": [],
            "entities": []
        }
        
        # Extract named entities
        for ent in doc.ents:
            entity_data = {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            result["entities"].append(entity_data)
            
            # Map entity types
            if ent.label_ in ["GPE", "LOC", "COUNTRY"]:
                result["origins"].append(ent.text)
            elif ent.label_ in ["ORG", "PRODUCT"]:
                # Could be ingredient or brand
                pass
        
        # Extract noun chunks as potential ingredients
        for chunk in doc.noun_chunks:
            text_lower = chunk.text.lower()
            
            # Check for materials
            for material in self.MATERIAL_KEYWORDS:
                if material in text_lower:
                    result["materials"].append(chunk.text)
                    break
        
        return result
    
    def _regex_extraction(self, text: str) -> Dict[str, Any]:
        """
        Extract entities using regex patterns
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with extracted entities
        """
        result = {
            "ingredients": [],
            "materials": [],
            "origins": [],
            "labels": []
        }
        
        text_lower = text.lower()
        
        # Extract ingredients section
        for pattern in self.INGREDIENT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                ingredients_text = match.group(1)
                # Split by common delimiters
                ingredients = re.split(r'[,;•\n]', ingredients_text)
                result["ingredients"] = [
                    ing.strip() for ing in ingredients 
                    if ing.strip() and len(ing.strip()) > 1
                ]
                break
        
        # Extract labels
        for label_type, keywords in self.LABEL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    result["labels"].append(label_type)
                    break
        
        # Extract materials
        for material in self.MATERIAL_KEYWORDS:
            if material in text_lower:
                result["materials"].append(material)
        
        return result
    
    def parse_ingredients_list(self, ingredients_text: str) -> List[Dict[str, Any]]:
        """
        Parse an ingredients list into structured data
        
        Args:
            ingredients_text: Raw ingredients text
            
        Returns:
            List of parsed ingredients with quantities
        """
        ingredients = []
        
        # Split by common delimiters
        parts = re.split(r'[,;•]', ingredients_text)
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue
            
            # Try to extract percentage
            percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%', part)
            percentage = None
            if percentage_match:
                percentage = float(percentage_match.group(1))
                part = re.sub(r'\d+(?:\.\d+)?\s*%', '', part).strip()
            
            # Clean ingredient name
            ingredient_name = re.sub(r'[*†‡]', '', part).strip()
            ingredient_name = re.sub(r'\s+', ' ', ingredient_name)
            
            if ingredient_name:
                ingredients.append({
                    "name": ingredient_name,
                    "percentage": percentage,
                    "original_text": part
                })
        
        return ingredients
