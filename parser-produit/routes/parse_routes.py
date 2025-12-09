"""
API routes for product parsing
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from services.pdf_parser import PDFParser
from services.html_parser import HTMLParser
from services.image_parser import ImageParser
from services.barcode_reader import BarcodeReader
from services.product_lookup import ProductLookupService
from models.product import ProductParsed, ProductParsedCreate
from database.connection import get_db
from database.crud import create_parsed_product, get_parsed_product

logger = logging.getLogger(__name__)
router = APIRouter()

pdf_parser = PDFParser()
html_parser = HTMLParser()
image_parser = ImageParser()
barcode_reader = BarcodeReader()
product_lookup = ProductLookupService()


def detect_file_type(filename: str, content_type: str) -> str:
    """Detect file type from filename and content type"""
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf') or content_type == 'application/pdf':
        return 'pdf'
    elif filename_lower.endswith(('.html', '.htm')) or 'html' in content_type:
        return 'html'
    elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
        return 'image'
    else:
        return 'unknown'


@router.post("/parse")
async def parse_product(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Parse product data from uploaded file (PDF, HTML, or image)
    
    Returns normalized JSON containing:
    - title
    - brand
    - ingredients_text
    - packaging
    - origin
    - gtin
    - raw_text
    """
    logger.info(f"Parsing file: {file.filename} (type: {file.content_type})")
    try:
        content = await file.read()
        file_type = detect_file_type(file.filename, file.content_type)
        logger.debug(f"Detected file type: {file_type}")
        
        result = {
            "title": None,
            "brand": None,
            "ingredients_text": None,
            "packaging": None,
            "origin": None,
            "gtin": None,
            "raw_text": None
        }
        
        if file_type == 'pdf':
            parsed_data = pdf_parser.parse(content)
            result.update(parsed_data)
            
        elif file_type == 'html':
            parsed_data = html_parser.parse(content.decode('utf-8', errors='ignore'))
            result.update(parsed_data)
            
        elif file_type == 'image':
            # Extract text via OCR
            ocr_data = image_parser.extract_text(content)
            result["raw_text"] = ocr_data.get("text", "")
            
            # Try to detect barcode/GTIN first
            barcode_data = barcode_reader.read_barcode(content)
            if barcode_data:
                result["gtin"] = barcode_data.get("gtin")
                logger.info(f"Detected barcode: {result['gtin']}")
                
                # Look up product info from external database
                try:
                    lookup_data = await product_lookup.lookup_by_gtin(result["gtin"])
                    if lookup_data:
                        # Use lookup data as base, but keep OCR data if available
                        logger.info(f"Found product in external database: {lookup_data.get('title')}")
                        result["title"] = lookup_data.get("title") or result.get("title")
                        result["brand"] = lookup_data.get("brand") or result.get("brand")
                        result["ingredients_text"] = lookup_data.get("ingredients_text") or result.get("ingredients_text")
                        result["packaging"] = lookup_data.get("packaging") or result.get("packaging")
                        result["origin"] = lookup_data.get("origin") or result.get("origin")
                        
                        # Add extra metadata from lookup
                        result["categories"] = lookup_data.get("categories")
                        result["labels"] = lookup_data.get("labels")
                        result["image_url"] = lookup_data.get("image_url")
                        result["source"] = lookup_data.get("source")
                    else:
                        logger.warning(f"No product found in external databases for GTIN: {result['gtin']}")
                except Exception as e:
                    logger.error(f"Error during product lookup: {str(e)}")
            
            # Extract structured data from OCR text (if no lookup data or as fallback)
            structured = image_parser.extract_structured_data(ocr_data.get("text", ""))
            # Only update fields that are still None
            for key, value in structured.items():
                if result.get(key) is None and value is not None:
                    result[key] = value
            
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.filename}"
            )
        
        # Store in database
        product_data = ProductParsedCreate(
            filename=file.filename,
            file_type=file_type,
            title=result.get("title"),
            brand=result.get("brand"),
            ingredients_text=result.get("ingredients_text"),
            packaging=result.get("packaging"),
            origin=result.get("origin"),
            gtin=result.get("gtin"),
            raw_text=result.get("raw_text")
        )
        
        db_product = create_parsed_product(db, product_data)
        result["id"] = str(db_product.id)
        logger.info(f"Successfully parsed and stored product: {file.filename} (ID: {result['id']})")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")


@router.post("/parse/batch")
async def parse_product_batch(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Parse multiple product files at once (batch processing)
    
    Returns list of parsed products with their IDs
    """
    logger.info(f"Batch parsing {len(files)} files")
    results = []
    errors = []
    
    for file in files:
        try:
            content = await file.read()
            file_type = detect_file_type(file.filename, file.content_type)
            
            result = {
                "title": None,
                "brand": None,
                "ingredients_text": None,
                "packaging": None,
                "origin": None,
                "gtin": None,
                "raw_text": None,
                "filename": file.filename
            }
            
            if file_type == 'pdf':
                parsed_data = pdf_parser.parse(content)
                result.update(parsed_data)
            elif file_type == 'html':
                parsed_data = html_parser.parse(content.decode('utf-8', errors='ignore'))
                result.update(parsed_data)
            elif file_type == 'image':
                ocr_data = image_parser.extract_text(content)
                result["raw_text"] = ocr_data.get("text", "")
                barcode_data = barcode_reader.read_barcode(content)
                if barcode_data:
                    result["gtin"] = barcode_data.get("gtin")
                structured = image_parser.extract_structured_data(ocr_data.get("text", ""))
                result.update(structured)
            else:
                errors.append({"filename": file.filename, "error": "Unsupported file type"})
                continue
            
            # Validate and clean GTIN
            if result.get("gtin"):
                result["gtin"] = _validate_gtin(result["gtin"])
            
            # Store in database
            product_data = ProductParsedCreate(
                filename=file.filename,
                file_type=file_type,
                title=result.get("title"),
                brand=result.get("brand"),
                ingredients_text=result.get("ingredients_text"),
                packaging=result.get("packaging"),
                origin=result.get("origin"),
                gtin=result.get("gtin"),
                raw_text=result.get("raw_text")
            )
            
            db_product = create_parsed_product(db, product_data)
            result["id"] = str(db_product.id)
            result["status"] = "success"
            results.append(result)
            
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})
    
    logger.info(f"Batch parsing complete: {len(results)} success, {len(errors)} failed")
    return {
        "total": len(files),
        "success": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@router.get("/parsed/{product_id}")
async def get_parsed_product_by_id(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve a previously parsed product by ID"""
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    product = get_parsed_product(db, product_uuid)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": str(product.id),
        "title": product.title,
        "brand": product.brand,
        "ingredients_text": product.ingredients_text,
        "packaging": product.packaging,
        "origin": product.origin,
        "gtin": product.gtin,
        "raw_text": product.raw_text,
        "created_at": product.created_at.isoformat()
    }


@router.get("/stats")
async def get_parsing_stats(db: Session = Depends(get_db)):
    """
    Get parsing statistics
    
    Returns counts and metrics about parsed products
    """
    from database.crud import get_parsing_stats
    return get_parsing_stats(db)


@router.get("/gtin/{gtin}")
async def get_product_by_gtin(
    gtin: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a product by GTIN/EAN code
    
    Validates GTIN format before searching
    """
    logger.debug(f"GTIN search request: {gtin}")
    # Validate GTIN format
    cleaned_gtin = _validate_gtin(gtin)
    if not cleaned_gtin:
        logger.warning(f"Invalid GTIN format: {gtin}")
        raise HTTPException(
            status_code=400, 
            detail="Invalid GTIN format. Must be 8, 12, 13, or 14 digits"
        )
    
    from database.crud import get_parsed_product_by_gtin
    product = get_parsed_product_by_gtin(db, cleaned_gtin)
    
    if not product:
        logger.info(f"No product found with GTIN: {cleaned_gtin}")
        raise HTTPException(
            status_code=404, 
            detail=f"No product found with GTIN {cleaned_gtin}"
        )
    
    logger.info(f"Product found for GTIN {cleaned_gtin}: {product.title}")
    return {
        "id": str(product.id),
        "title": product.title,
        "brand": product.brand,
        "ingredients_text": product.ingredients_text,
        "packaging": product.packaging,
        "origin": product.origin,
        "gtin": product.gtin,
        "raw_text": product.raw_text,
        "created_at": product.created_at.isoformat()
    }


def _validate_gtin(gtin: str) -> Optional[str]:
    """
    Validate and clean GTIN/EAN/UPC code
    
    Args:
        gtin: GTIN string to validate
        
    Returns:
        Cleaned GTIN or None if invalid
    """
    if not gtin:
        return None
    
    # Remove spaces, dashes, and other non-numeric characters
    cleaned = ''.join(c for c in str(gtin) if c.isdigit())
    
    # Check if length is valid (GTIN-8, UPC-12, GTIN-13, GTIN-14)
    if len(cleaned) not in [8, 12, 13, 14]:
        return None
    
    # TODO: Implement checksum validation for GTIN
    
    return cleaned
