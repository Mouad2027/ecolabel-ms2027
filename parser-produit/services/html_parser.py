"""
HTML Parser Service
Extracts product data from HTML content using BeautifulSoup
"""

import re
from typing import Dict, Any, Optional, List

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class HTMLParser:
    """Service for parsing HTML documents and extracting product data"""
    
    def __init__(self):
        # Common selectors for product data
        self.title_selectors = [
            'h1.product-title',
            'h1.product-name',
            '.product-title',
            '.product-name',
            '[itemprop="name"]',
            'h1',
            'title'
        ]
        
        self.brand_selectors = [
            '.brand',
            '.product-brand',
            '[itemprop="brand"]',
            '.manufacturer',
            '[data-brand]'
        ]
        
        self.ingredients_selectors = [
            '.ingredients',
            '.product-ingredients',
            '[itemprop="ingredients"]',
            '#ingredients',
            '.ingredient-list',
            '.composition'
        ]
        
        self.packaging_selectors = [
            '.packaging',
            '.product-packaging',
            '.container-info',
            '.pack-info'
        ]
        
        self.origin_selectors = [
            '.origin',
            '.country-of-origin',
            '[itemprop="countryOfOrigin"]',
            '.made-in'
        ]
        
        self.gtin_selectors = [
            '[itemprop="gtin13"]',
            '[itemprop="gtin"]',
            '[data-gtin]',
            '[data-ean]',
            '.gtin',
            '.ean',
            '.barcode'
        ]
    
    def parse(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract product data
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Dictionary with extracted fields
        """
        if not BS4_AVAILABLE:
            raise RuntimeError("BeautifulSoup4 is not installed. Install it with: pip install beautifulsoup4")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        raw_text = soup.get_text(separator='\n', strip=True)
        
        return {
            "title": self._extract_by_selectors(soup, self.title_selectors),
            "brand": self._extract_by_selectors(soup, self.brand_selectors),
            "ingredients_text": self._extract_by_selectors(soup, self.ingredients_selectors),
            "packaging": self._extract_by_selectors(soup, self.packaging_selectors),
            "origin": self._extract_by_selectors(soup, self.origin_selectors),
            "gtin": self._extract_gtin(soup),
            "raw_text": raw_text[:10000]  # Limit raw text size
        }
    
    def _extract_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
        """
        Try multiple CSS selectors to extract content
        
        Args:
            soup: BeautifulSoup object
            selectors: List of CSS selectors to try
            
        Returns:
            Extracted text or None
        """
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return self._clean_text(text)
            except Exception:
                continue
        return None
    
    def _extract_gtin(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract GTIN/EAN/UPC from HTML
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            GTIN string or None
        """
        # Try selectors first
        for selector in self.gtin_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    # Check for data attributes
                    for attr in ['data-gtin', 'data-ean', 'content', 'value']:
                        value = element.get(attr)
                        if value and re.match(r'^\d{8,14}$', str(value)):
                            return str(value)
                    
                    # Check text content
                    text = element.get_text(strip=True)
                    if text and re.match(r'^\d{8,14}$', text):
                        return text
            except Exception:
                continue
        
        # Try to find GTIN in meta tags
        meta_patterns = [
            ('meta[property="product:gtin"]', 'content'),
            ('meta[name="gtin"]', 'content'),
            ('meta[itemprop="gtin13"]', 'content'),
        ]
        
        for selector, attr in meta_patterns:
            try:
                element = soup.select_one(selector)
                if element:
                    value = element.get(attr)
                    if value and re.match(r'^\d{8,14}$', str(value)):
                        return str(value)
            except Exception:
                continue
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common HTML artifacts
        text = text.strip()
        return text
    
    def extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract JSON-LD structured data if available
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with structured data
        """
        import json
        
        result = {}
        
        # Look for JSON-LD scripts
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get('@type') == 'Product':
                        result['title'] = data.get('name')
                        result['brand'] = data.get('brand', {}).get('name') if isinstance(data.get('brand'), dict) else data.get('brand')
                        result['gtin'] = data.get('gtin13') or data.get('gtin')
                        break
            except (json.JSONDecodeError, TypeError):
                continue
        
        return result
