"""
PDF Parser Service
Extracts text and structured data from PDF files
"""

import io
import re
from typing import Dict, Any, Optional

try:
    from pdfminer.high_level import extract_text
    from pdfminer.pdfparser import PDFParser as PDFMinerParser
    from pdfminer.pdfdocument import PDFDocument
    PDF_MINER_AVAILABLE = True
except ImportError:
    PDF_MINER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class PDFParser:
    """Service for parsing PDF documents"""
    
    def __init__(self):
        self.ingredient_patterns = [
            r'(?:ingredients?|composition|ingrédients?)\s*[:\-]?\s*(.+?)(?=\n\n|\Z)',
            r'(?:contains?|contient)\s*[:\-]?\s*(.+?)(?=\n\n|\Z)',
        ]
        self.title_patterns = [
            r'^([A-Z][A-Za-z\s\-]+)(?:\n|$)',
            r'(?:product|produit|name|nom)\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
        self.brand_patterns = [
            r'(?:brand|marque|by|par)\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
        self.origin_patterns = [
            r'(?:origin|origine|made in|fabriqué en|country)\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
        self.packaging_patterns = [
            r'(?:packaging|emballage|container)\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
        self.gtin_patterns = [
            r'(?:gtin|ean|upc|barcode)\s*[:\-]?\s*(\d{8,14})',
            r'\b(\d{13})\b',  # EAN-13
            r'\b(\d{12})\b',  # UPC-A
        ]
    
    def parse(self, content: bytes) -> Dict[str, Any]:
        """
        Parse PDF content and extract structured data
        
        Args:
            content: Raw PDF file bytes
            
        Returns:
            Dictionary with extracted fields
        """
        raw_text = self._extract_text(content)
        
        return {
            "title": self._extract_field(raw_text, self.title_patterns),
            "brand": self._extract_field(raw_text, self.brand_patterns),
            "ingredients_text": self._extract_field(raw_text, self.ingredient_patterns),
            "packaging": self._extract_field(raw_text, self.packaging_patterns),
            "origin": self._extract_field(raw_text, self.origin_patterns),
            "gtin": self._extract_field(raw_text, self.gtin_patterns),
            "raw_text": raw_text
        }
    
    def _extract_text(self, content: bytes) -> str:
        """Extract raw text from PDF using available library"""
        if PDF_MINER_AVAILABLE:
            return self._extract_with_pdfminer(content)
        elif PYPDF2_AVAILABLE:
            return self._extract_with_pypdf2(content)
        else:
            # TODO: Implement fallback or raise appropriate error
            raise RuntimeError("No PDF parsing library available. Install pdfminer.six or PyPDF2")
    
    def _extract_with_pdfminer(self, content: bytes) -> str:
        """Extract text using pdfminer"""
        try:
            return extract_text(io.BytesIO(content))
        except Exception as e:
            # TODO: Add proper logging
            return f"Error extracting PDF text: {str(e)}"
    
    def _extract_with_pypdf2(self, content: bytes) -> str:
        """Extract text using PyPDF2"""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        except Exception as e:
            # TODO: Add proper logging
            return f"Error extracting PDF text: {str(e)}"
    
    def _extract_field(self, text: str, patterns: list) -> Optional[str]:
        """
        Extract a field from text using regex patterns
        
        Args:
            text: Source text
            patterns: List of regex patterns to try
            
        Returns:
            Extracted value or None
        """
        if not text:
            return None
            
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                # Clean up the value
                value = re.sub(r'\s+', ' ', value)
                if value:
                    return value
        return None
