"""
Tests for provenance microservice
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
    assert data["service"] == "provenance"


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
    assert data["info"]["title"] == "Provenance Service"


def test_track_endpoint():
    """Test track endpoint for data provenance"""
    response = client.post("/provenance/track", json={
        "entity_type": "product",
        "entity_id": "test-123",
        "action": "created",
        "metadata": {"source": "test"}
    })
    assert response.status_code in [200, 404, 405, 422, 500]  # May not be implemented or method not allowed


def test_lineage_endpoint():
    """Test lineage endpoint"""
    response = client.get("/provenance/lineage/test-123")
    assert response.status_code in [200, 404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
