"""
Tests for parser-produit microservice
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
import io

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "parser-produit"


def test_parse_endpoint_no_file():
    """Test parse endpoint without file"""
    response = client.post("/product/parse")
    assert response.status_code == 422  # Unprocessable Entity


def test_parse_endpoint_with_text_file():
    """Test parse endpoint with simple text file"""
    files = {"file": ("test.txt", b"Test product data", "text/plain")}
    response = client.post("/product/parse", files=files)
    # May fail but should not crash
    assert response.status_code in [200, 400, 422]


def test_batch_parse_endpoint_no_files():
    """Test batch parse endpoint without files"""
    response = client.post("/product/parse/batch")
    assert response.status_code == 422  # Unprocessable Entity


def test_batch_parse_endpoint_with_files():
    """Test batch parse endpoint with multiple files"""
    files = [
        ("files", ("test1.txt", b"Product 1 GTIN: 1234567890123", "text/plain")),
        ("files", ("test2.txt", b"Product 2 Brand: TestBrand", "text/plain"))
    ]
    response = client.post("/product/parse/batch", files=files)
    # Should return results even if some fail
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "errors" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["errors"], list)


def test_gtin_search_endpoint():
    """Test GTIN search endpoint"""
    # Test with valid GTIN format
    response = client.get("/product/gtin/1234567890123")
    # May return 404 if not found, 200 if found
    assert response.status_code in [200, 404]


def test_gtin_search_invalid():
    """Test GTIN search with invalid format"""
    response = client.get("/product/gtin/invalid")
    # Should return error for invalid GTIN
    assert response.status_code in [400, 404]


def test_stats_endpoint():
    """Test statistics endpoint"""
    response = client.get("/product/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "by_file_type" in data
    assert "products_with_gtin" in data
    assert "products_with_ingredients" in data
    assert isinstance(data["total_products"], int)


def test_api_docs():
    """Test API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test OpenAPI schema is valid"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert data["info"]["title"] == "Parser-Produit Service"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
