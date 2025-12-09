"""
Product Lookup Service
Fetches product information from external databases using GTIN/barcode
"""

import httpx
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ProductLookupService:
    """Service for looking up product information from external APIs"""
    
    # OpenFoodFacts API endpoints
    OPENFOODFACTS_API = "https://world.openfoodfacts.org/api/v2/product"
    OPENFOODFACTS_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"
    
    def __init__(self, timeout: int = 10):
        """
        Initialize ProductLookupService
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            "User-Agent": "EcoLabel-MS - Product Scanner - Version 1.0"
        }
    
    async def lookup_by_gtin(self, gtin: str) -> Optional[Dict[str, Any]]:
        """
        Look up product information by GTIN/barcode
        
        Args:
            gtin: Product GTIN/EAN/UPC code
            
        Returns:
            Dictionary with product information or None
        """
        # Clean GTIN (remove spaces, hyphens)
        gtin_clean = gtin.replace(" ", "").replace("-", "")
        
        # Try OpenFoodFacts first
        result = await self._lookup_openfoodfacts(gtin_clean)
        
        if result:
            return result
        
        # Could add more APIs here (GS1, other databases)
        logger.warning(f"No product found for GTIN: {gtin}")
        return None
    
    async def _lookup_openfoodfacts(self, gtin: str) -> Optional[Dict[str, Any]]:
        """
        Look up product in OpenFoodFacts database
        
        Args:
            gtin: Clean GTIN code
            
        Returns:
            Normalized product data or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.OPENFOODFACTS_API}/{gtin}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.debug(f"OpenFoodFacts returned {response.status_code} for GTIN {gtin}")
                    return None
                
                data = response.json()
                
                # Check if product was found
                if data.get("status") != 1 or not data.get("product"):
                    logger.debug(f"Product not found in OpenFoodFacts: {gtin}")
                    return None
                
                product = data["product"]
                
                # Extract and normalize product information
                result = {
                    "title": self._get_product_name(product),
                    "brand": self._get_brand(product),
                    "ingredients_text": self._get_ingredients(product),
                    "packaging": self._get_packaging(product),
                    "origin": self._get_origin(product),
                    "gtin": gtin,
                    "categories": product.get("categories", ""),
                    "labels": product.get("labels", ""),
                    "image_url": product.get("image_url"),
                    "nutriscore": product.get("nutriscore_grade"),
                    "ecoscore": product.get("ecoscore_grade"),
                    "source": "OpenFoodFacts",
                    "data_quality": product.get("data_quality_tags", [])
                }
                
                logger.info(f"Found product in OpenFoodFacts: {result['title']} ({gtin})")
                return result
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout looking up product {gtin} in OpenFoodFacts")
            return None
        except Exception as e:
            logger.error(f"Error looking up product {gtin}: {str(e)}")
            return None
    
    def _get_product_name(self, product: dict) -> Optional[str]:
        """Extract product name from OpenFoodFacts data"""
        # Try different name fields in order of preference
        name = (
            product.get("product_name") or
            product.get("product_name_en") or
            product.get("product_name_fr") or
            product.get("generic_name") or
            product.get("abbreviated_product_name")
        )
        return name.strip() if name else None
    
    def _get_brand(self, product: dict) -> Optional[str]:
        """Extract brand from OpenFoodFacts data"""
        brands = product.get("brands")
        if brands:
            # Take first brand if multiple
            return brands.split(",")[0].strip()
        return None
    
    def _get_ingredients(self, product: dict) -> Optional[str]:
        """Extract ingredients text from OpenFoodFacts data"""
        # Try different ingredient fields
        ingredients = (
            product.get("ingredients_text") or
            product.get("ingredients_text_en") or
            product.get("ingredients_text_fr")
        )
        return ingredients.strip() if ingredients else None
    
    def _get_packaging(self, product: dict) -> Optional[str]:
        """Extract packaging information from OpenFoodFacts data"""
        packaging = product.get("packaging")
        if packaging:
            return packaging.strip()
        
        # Alternative: packaging_tags
        packaging_tags = product.get("packaging_tags", [])
        if packaging_tags:
            return ", ".join(packaging_tags)
        
        return None
    
    def _get_origin(self, product: dict) -> Optional[str]:
        """Extract origin/country from OpenFoodFacts data"""
        # Try multiple fields
        origin = (
            product.get("origins") or
            product.get("manufacturing_places") or
            product.get("countries")
        )
        
        if origin:
            return origin.split(",")[0].strip()
        
        return None
    
    async def search_by_name(self, query: str, limit: int = 5) -> list:
        """
        Search products by name
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching products
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.OPENFOODFACTS_SEARCH,
                    params={
                        "search_terms": query,
                        "json": 1,
                        "page_size": limit,
                        "fields": "product_name,brands,code,image_url"
                    },
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    products = data.get("products", [])
                    
                    return [
                        {
                            "title": p.get("product_name"),
                            "brand": p.get("brands"),
                            "gtin": p.get("code"),
                            "image_url": p.get("image_url")
                        }
                        for p in products
                    ]
                
                return []
                
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
