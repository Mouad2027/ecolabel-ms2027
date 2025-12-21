# EcoLabel-MS Features Documentation

## File Upload Feature

### Overview
Frontend widget allows users to upload product images, PDFs, or HTML files for automatic product information extraction.

### Supported File Types
- **PDF** - Product labels, technical specifications
- **HTML** - Product web pages
- **Images** - Product photos, photographed labels
  - JPG / JPEG
  - PNG
  - GIF
  - BMP
  - TIFF

### Upload Methods
1. **Drag & Drop** - Drag files directly onto the upload zone
2. **Browse** - Click button to open file selector

### Automatic Extraction
The system automatically extracts:
- ✅ Product title
- ✅ Brand
- ✅ GTIN/EAN barcode
- ✅ Origin
- ✅ Packaging
- ✅ Ingredients list

---

## Parser-Produit Enhanced Features

### Batch Processing
**Endpoint:** `POST /product/parse/batch`

- Process multiple files in a single request
- Individual error tracking per file
- Aggregated results with success/failure counts
- Prevents one bad file from blocking others

**Example:**
```bash
curl -X POST "http://localhost:8001/product/parse/batch" \
  -F "files=@product1.pdf" \
  -F "files=@product2.html" \
  -F "files=@product3.jpg"
```

### GTIN Search
**Endpoint:** `GET /product/gtin/{gtin}`

- Search products by barcode
- Input validation and cleaning
- Supports GTIN-8, GTIN-12, GTIN-13, GTIN-14

### Statistics Endpoint
**Endpoint:** `GET /product/stats`

Returns:
- Total product counts
- Breakdown by file type (PDF/HTML/Image)
- Products with GTIN count
- Products with ingredients count

### Structured Logging
- Application lifecycle tracking
- Request/response logging
- Error tracking with context
- Performance monitoring

---

## Testing Infrastructure

### Test Coverage
- **30 tests** created across 5 microservices
- **100% success rate** on all tests
- Complete framework with pytest and httpx

### Services Tested
1. **Parser-Produit**: 5 tests
2. **NLP-Ingredients**: 6 tests
3. **LCA-Lite**: 6 tests
4. **Scoring**: 6 tests
5. **Provenance**: 7 tests

### Running Tests
```bash
# Run all tests
.\run-tests.ps1

# Run specific service tests
cd parser-produit
pytest tests/
```

---

## Deployment

### Docker Deployment
- **10 services** deployed and operational
- Complete infrastructure (PostgreSQL, MinIO, MLflow)
- Health checks functional on all services

### Demo Data
- **5 test products** inserted in database
- Eco-scores calculated (A, B, C, D)
- Functional search via API and frontend

### Services
| Service | Port | Status |
|---------|------|--------|
| Parser | 8001 | ✅ |
| NLP | 8002 | ✅ |
| LCA | 8003 | ✅ |
| Scoring | 8004 | ✅ |
| Widget API | 8005 | ✅ |
| Provenance | 8006 | ✅ |
| Frontend | 3000 | ✅ |
| PostgreSQL | 5432 | ✅ |
| MinIO | 9000/9001 | ✅ |
| MLflow | 5000 | ✅ |
