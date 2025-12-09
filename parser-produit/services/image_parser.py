"""
Image Parser Service
Extracts text from images using Tesseract OCR
"""

import io
import re
from typing import Dict, Any, Optional

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class ImageParser:
    """Service for extracting text from images using OCR"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize ImageParser
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        if tesseract_cmd and TESSERACT_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Regex patterns for structured data extraction
        self.ingredient_patterns = [
            r'(?:ingredients?|composition|ingrédients?)\s*[:\-]?\s*(.+?)(?=\n\n|\Z)',
            r'(?:contains?|contient)\s*[:\-]?\s*(.+?)(?=\n\n|\Z)',
        ]
        self.title_patterns = [
            r'^([A-Z][A-Za-z\s\-]+)(?:\n|$)',
        ]
        self.brand_patterns = [
            r'(?:brand|marque|by|par)\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
        self.origin_patterns = [
            r'(?:origin|origine|made in|fabriqué en)\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
        self.packaging_patterns = [
            r'(?:packaging|emballage)\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
    
    def extract_text(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract text from image using OCR
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError(
                "Tesseract OCR is not available. "
                "Install pytesseract and Tesseract: pip install pytesseract pillow"
            )
        
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image for better OCR results
            image = self._preprocess_image(image)
            
            # Extract text with multiple language support
            text = pytesseract.image_to_string(
                image,
                lang='eng+fra+deu+spa+ita',  # Multiple languages
                config='--psm 6'  # Assume uniform block of text
            )
            
            # Get OCR confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": text.strip(),
                "confidence": avg_confidence,
                "image_size": image.size,
                "image_mode": image.mode
            }
            
        except Exception as e:
            # TODO: Add proper logging
            return {
                "text": "",
                "error": str(e),
                "confidence": 0
            }
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to RGB if necessary
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Convert to grayscale
        if image.mode == 'RGB':
            image = image.convert('L')
        
        # Resize if too small
        min_dimension = 1000
        if min(image.size) < min_dimension:
            ratio = min_dimension / min(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured product data from OCR text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with structured fields
        """
        if not text:
            return {}
        
        return {
            "title": self._extract_field(text, self.title_patterns),
            "brand": self._extract_field(text, self.brand_patterns),
            "ingredients_text": self._extract_field(text, self.ingredient_patterns),
            "packaging": self._extract_field(text, self.packaging_patterns),
            "origin": self._extract_field(text, self.origin_patterns),
        }
    
    def _extract_field(self, text: str, patterns: list) -> Optional[str]:
        """
        Extract a field from text using regex patterns
        
        Args:
            text: Source text
            patterns: List of regex patterns to try
            
        Returns:
            Extracted value or None
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                value = re.sub(r'\s+', ' ', value)
                if value:
                    return value
        return None
    
    def detect_text_regions(self, image_data: bytes) -> list:
        """
        Detect text regions in image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            List of detected text regions with bounding boxes
        """
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            image = Image.open(io.BytesIO(image_data))
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            regions = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                if int(data['conf'][i]) > 60:  # Filter by confidence
                    regions.append({
                        "text": data['text'][i],
                        "confidence": int(data['conf'][i]),
                        "bbox": {
                            "x": data['left'][i],
                            "y": data['top'][i],
                            "width": data['width'][i],
                            "height": data['height'][i]
                        }
                    })
            
            return regions
            
        except Exception:
            return []
