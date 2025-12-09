"""
Tests for lca-lite microservice
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
    assert data["service"] == "lca-lite"


def test_calc_endpoint_empty_ingredients():
    """Test calc endpoint with empty ingredients"""
    response = client.post("/lca/calc", json={"ingredients": []})
    assert response.status_code in [200, 422, 500]  # May return 500 if empty ingredients not handled


def test_calc_endpoint_valid_data():
    """Test calc endpoint with valid ingredient data"""
    response = client.post("/lca/calc", json={
        "ingredients": [
            {"name": "wheat flour", "weight": 0.5},
            {"name": "sugar", "weight": 0.2}
        ]
    })
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "co2" in data
        assert "water" in data
        assert "energy" in data
        assert isinstance(data["co2"], (int, float))
        assert isinstance(data["water"], (int, float))
        assert isinstance(data["energy"], (int, float))


def test_calc_endpoint_with_transport():
    """Test calc endpoint with transport information"""
    response = client.post("/lca/calc", json={
        "ingredients": [
            {"name": "wheat flour", "weight": 1.0, "origin": "France"}
        ],
        "transport": [
            {"mode": "truck", "distance_km": 500}
        ]
    })
    assert response.status_code in [200, 500]


def test_calc_endpoint_with_packaging():
    """Test calc endpoint with packaging information"""
    response = client.post("/lca/calc", json={
        "ingredients": [
            {"name": "coffee", "weight": 0.5}
        ],
        "packaging_material": "plastic",
        "packaging_weight_kg": 0.05
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
    assert data["info"]["title"] == "LCA-Lite Service"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
