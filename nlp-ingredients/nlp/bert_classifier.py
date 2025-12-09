"""
BERT Classifier for entity classification
Uses multilingual BERT for classifying extracted entities
"""

from typing import Dict, List, Any, Optional
import re

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class BertClassifier:
    """
    BERT-based classifier for enhancing entity extraction
    Uses multilingual BERT for multi-language support
    """
    
    # Entity categories
    CATEGORIES = [
        "ingredient",
        "packaging_material",
        "origin",
        "label",
        "brand",
        "other"
    ]
    
    # Label classification keywords
    LABEL_INDICATORS = {
        "bio": ["bio", "organic", "biologique", "ökologisch", "biologico", "ecológico"],
        "recyclable": ["recyclable", "recycled", "recyclé", "recycliert", "reciclable"],
        "vegan": ["vegan", "végétalien", "végane", "vegano"],
        "vegetarian": ["vegetarian", "végétarien", "vegetariano"],
        "fair_trade": ["fair trade", "fairtrade", "commerce équitable", "comercio justo"],
        "non_gmo": ["non-gmo", "sans ogm", "gmo-free", "ohne gentechnik"],
        "gluten_free": ["gluten-free", "sans gluten", "glutenfrei", "sin gluten"],
        "lactose_free": ["lactose-free", "sans lactose", "laktosefrei"],
        "palm_oil_free": ["palm oil free", "sans huile de palme"],
        "sustainable": ["sustainable", "durable", "nachhaltig", "sostenible"],
        "eco_friendly": ["eco-friendly", "écologique", "umweltfreundlich"]
    }
    
    # Material indicators
    MATERIAL_INDICATORS = [
        "plastic", "plastique", "kunststoff", "plástico",
        "glass", "verre", "glas", "vidrio",
        "metal", "métal", "metall",
        "aluminum", "aluminium", "alu",
        "cardboard", "carton", "karton", "cartón",
        "paper", "papier", "papel",
        "wood", "bois", "holz", "madera",
        "tin", "étain", "zinn",
        "steel", "acier", "stahl", "acero",
        "pet", "hdpe", "ldpe", "pp", "ps", "pvc",
        "tetra pak", "tetrapack",
        "biodegradable", "compostable"
    ]
    
    def __init__(self, model_name: str = "bert-base-multilingual-cased"):
        """
        Initialize BERT classifier
        
        Args:
            model_name: Hugging Face model name
        """
        self.model_name = model_name
        self.classifier = None
        self.tokenizer = None
        self._initialized = False
        
        # Don't load model at init - lazy loading for faster startup
    
    def _ensure_initialized(self):
        """Lazy initialization of the model"""
        if self._initialized:
            return
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use zero-shot classification pipeline for flexibility
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=-1  # CPU
                )
                self._initialized = True
            except Exception as e:
                # TODO: Add proper logging
                self._initialized = False
    
    def classify_entities(
        self, 
        text: str, 
        spacy_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify and enhance entities extracted by spaCy
        
        Args:
            text: Original text
            spacy_results: Results from spaCy extraction
            
        Returns:
            Enhanced extraction results
        """
        result = {
            "ingredients": spacy_results.get("ingredients", []).copy(),
            "materials": spacy_results.get("materials", []).copy(),
            "origins": spacy_results.get("origins", []).copy(),
            "labels": spacy_results.get("labels", []).copy(),
            "confidence": 0.0
        }
        
        # Enhance with keyword-based classification
        text_lower = text.lower()
        
        # Extract labels
        detected_labels = self._extract_labels(text_lower)
        result["labels"] = list(set(result["labels"] + detected_labels))
        
        # Extract materials
        detected_materials = self._extract_materials(text_lower)
        result["materials"] = list(set(result["materials"] + detected_materials))
        
        # Use BERT for ingredient classification if available
        if TRANSFORMERS_AVAILABLE and self._should_use_bert(result):
            self._ensure_initialized()
            if self.classifier:
                bert_enhanced = self._bert_classification(text, result)
                result.update(bert_enhanced)
        
        # Calculate confidence
        result["confidence"] = self._calculate_confidence(result)
        
        return result
    
    def _should_use_bert(self, current_results: Dict) -> bool:
        """Determine if BERT classification would be helpful"""
        # Use BERT if we have few ingredients or uncertain results
        return len(current_results.get("ingredients", [])) < 3
    
    def _bert_classification(
        self, 
        text: str, 
        current_results: Dict
    ) -> Dict[str, Any]:
        """
        Use BERT for zero-shot classification
        
        Args:
            text: Input text
            current_results: Current extraction results
            
        Returns:
            Enhanced results
        """
        try:
            # Extract potential entities from text
            sentences = self._extract_sentences(text)
            
            for sentence in sentences[:5]:  # Limit to 5 sentences
                if len(sentence) < 10:
                    continue
                
                # Classify sentence
                result = self.classifier(
                    sentence,
                    candidate_labels=[
                        "ingredient list",
                        "packaging information",
                        "origin country",
                        "certification label"
                    ]
                )
                
                # Process classification result
                top_label = result["labels"][0]
                confidence = result["scores"][0]
                
                if confidence > 0.7:
                    if top_label == "ingredient list":
                        # Parse as ingredients
                        ingredients = self._parse_ingredients(sentence)
                        current_results["ingredients"].extend(ingredients)
            
            return current_results
            
        except Exception:
            return current_results
    
    def _extract_labels(self, text_lower: str) -> List[str]:
        """Extract certification labels from text"""
        labels = []
        
        for label_type, keywords in self.LABEL_INDICATORS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    labels.append(label_type)
                    break
        
        return labels
    
    def _extract_materials(self, text_lower: str) -> List[str]:
        """Extract packaging materials from text"""
        materials = []
        
        for material in self.MATERIAL_INDICATORS:
            if material in text_lower:
                materials.append(material)
        
        return materials
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?\n]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _parse_ingredients(self, text: str) -> List[str]:
        """Parse ingredients from text"""
        # Remove common prefixes
        text = re.sub(r'^(ingredients?|composition)\s*[:\-]?\s*', '', text, flags=re.IGNORECASE)
        
        # Split by delimiters
        ingredients = re.split(r'[,;•]', text)
        
        return [
            ing.strip() for ing in ingredients 
            if ing.strip() and len(ing.strip()) > 1 and len(ing.strip()) < 50
        ]
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate overall extraction confidence"""
        scores = []
        
        # More ingredients = higher confidence
        if result["ingredients"]:
            scores.append(min(len(result["ingredients"]) * 0.1, 0.5))
        
        # Having labels increases confidence
        if result["labels"]:
            scores.append(0.2)
        
        # Having materials increases confidence
        if result["materials"]:
            scores.append(0.2)
        
        # Having origins increases confidence
        if result["origins"]:
            scores.append(0.1)
        
        return min(sum(scores), 1.0) if scores else 0.0
    
    def classify_single_entity(self, entity_text: str) -> Dict[str, Any]:
        """
        Classify a single entity
        
        Args:
            entity_text: Text of the entity
            
        Returns:
            Classification result
        """
        self._ensure_initialized()
        
        if not self.classifier:
            return {"category": "unknown", "confidence": 0.0}
        
        try:
            result = self.classifier(
                entity_text,
                candidate_labels=self.CATEGORIES
            )
            
            return {
                "category": result["labels"][0],
                "confidence": result["scores"][0],
                "all_scores": dict(zip(result["labels"], result["scores"]))
            }
        except Exception:
            return {"category": "unknown", "confidence": 0.0}
