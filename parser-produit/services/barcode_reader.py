"""
Barcode Reader Service
Reads barcodes and extracts GTIN from images
"""

import io
from typing import Dict, Any, Optional, List

try:
    from pyzbar.pyzbar import decode
    from PIL import Image
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False


class BarcodeReader:
    """Service for reading barcodes from images"""
    
    # Barcode types that contain product identifiers
    PRODUCT_BARCODE_TYPES = [
        'EAN13',
        'EAN8', 
        'UPCA',
        'UPCE',
        'CODE128',
        'CODE39'
    ]
    
    def __init__(self):
        """Initialize BarcodeReader"""
        pass
    
    def read_barcode(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Read barcode from image and extract GTIN
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with barcode data or None
        """
        if not PYZBAR_AVAILABLE:
            # TODO: Add fallback barcode reader
            return None
        
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Decode barcodes
            barcodes = decode(image)
            
            if not barcodes:
                # Try with image preprocessing
                barcodes = self._try_with_preprocessing(image)
            
            if not barcodes:
                return None
            
            # Find the best barcode (prefer EAN-13)
            best_barcode = self._select_best_barcode(barcodes)
            
            if best_barcode:
                return {
                    "gtin": best_barcode.data.decode('utf-8'),
                    "type": best_barcode.type,
                    "quality": best_barcode.quality if hasattr(best_barcode, 'quality') else None,
                    "rect": {
                        "left": best_barcode.rect.left,
                        "top": best_barcode.rect.top,
                        "width": best_barcode.rect.width,
                        "height": best_barcode.rect.height
                    }
                }
            
            return None
            
        except Exception as e:
            # TODO: Add proper logging
            return None
    
    def read_all_barcodes(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        Read all barcodes from image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            List of barcode data dictionaries
        """
        if not PYZBAR_AVAILABLE:
            return []
        
        try:
            image = Image.open(io.BytesIO(image_data))
            barcodes = decode(image)
            
            results = []
            for barcode in barcodes:
                results.append({
                    "data": barcode.data.decode('utf-8'),
                    "type": barcode.type,
                    "rect": {
                        "left": barcode.rect.left,
                        "top": barcode.rect.top,
                        "width": barcode.rect.width,
                        "height": barcode.rect.height
                    }
                })
            
            return results
            
        except Exception:
            return []
    
    def _try_with_preprocessing(self, image: Image.Image) -> list:
        """
        Try barcode detection with image preprocessing
        
        Args:
            image: PIL Image object
            
        Returns:
            List of detected barcodes
        """
        try:
            # Convert to grayscale
            if image.mode != 'L':
                gray = image.convert('L')
            else:
                gray = image
            
            # Try with grayscale
            barcodes = decode(gray)
            if barcodes:
                return barcodes
            
            # Try with contrast enhancement
            from PIL import ImageEnhance
            
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)
            
            barcodes = decode(enhanced)
            if barcodes:
                return barcodes
            
            # Try with different thresholds
            thresholds = [100, 128, 150]
            for threshold in thresholds:
                binary = gray.point(lambda p: 255 if p > threshold else 0)
                barcodes = decode(binary)
                if barcodes:
                    return barcodes
            
            return []
            
        except Exception:
            return []
    
    def _select_best_barcode(self, barcodes: list):
        """
        Select the best barcode from detected barcodes
        Prioritizes EAN-13 and UPC-A
        
        Args:
            barcodes: List of detected barcodes
            
        Returns:
            Best barcode or None
        """
        if not barcodes:
            return None
        
        # Priority order
        priority = {
            'EAN13': 1,
            'UPCA': 2,
            'EAN8': 3,
            'UPCE': 4,
            'CODE128': 5,
            'CODE39': 6
        }
        
        # Filter to product barcodes only
        product_barcodes = [
            b for b in barcodes 
            if b.type in self.PRODUCT_BARCODE_TYPES
        ]
        
        if not product_barcodes:
            return barcodes[0] if barcodes else None
        
        # Sort by priority
        sorted_barcodes = sorted(
            product_barcodes,
            key=lambda b: priority.get(b.type, 100)
        )
        
        return sorted_barcodes[0]
    
    def validate_gtin(self, gtin: str) -> bool:
        """
        Validate GTIN checksum
        
        Args:
            gtin: GTIN string (8, 12, 13, or 14 digits)
            
        Returns:
            True if valid, False otherwise
        """
        if not gtin or not gtin.isdigit():
            return False
        
        if len(gtin) not in [8, 12, 13, 14]:
            return False
        
        # Pad to 14 digits
        gtin = gtin.zfill(14)
        
        # Calculate checksum
        total = 0
        for i, digit in enumerate(gtin[:-1]):
            multiplier = 3 if i % 2 == 0 else 1
            total += int(digit) * multiplier
        
        check_digit = (10 - (total % 10)) % 10
        
        return check_digit == int(gtin[-1])
