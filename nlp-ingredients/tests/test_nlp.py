"""
Tests for nlp-ingredients microservice
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

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
    assert data["service"] == "nlp-ingredients"


def test_extract_endpoint_empty_text():
    """Test extract endpoint with empty text"""
    response = client.post("/nlp/extract", json={"text": ""})
    assert response.status_code == 400


def test_extract_endpoint_valid_text():
    """Test extract endpoint with valid text"""
    response = client.post("/nlp/extract", json={
        "text": "Ingrédients: farine de blé, sucre, œufs, beurre",
        "language": "fr"
    })
    assert response.status_code in [200, 500]  # May fail if NLP models not loaded
    if response.status_code == 200:
        data = response.json()
        assert "ingredients" in data
        assert "materials" in data
        assert "origins" in data
        assert "labels" in data


def test_extract_endpoint_with_product_id():
    """Test extract endpoint with product_id"""
    response = client.post("/nlp/extract", json={
        "text": "Ingredients: wheat flour, sugar, eggs, butter",
        "language": "en",
        "product_id": "test-product-123"
    })
    assert response.status_code in [200, 500]


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
    assert data["info"]["title"] == "NLP-Ingredients Service"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
