"""API endpoint tests."""

import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test that the health endpoint returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_venues(client):
    """Test that the venues endpoint returns a list."""
    response = await client.get("/venues")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_events(client):
    """Test that the events endpoint returns a list."""
    response = await client.get("/events")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_venue(client):
    """Test creating a venue via API."""
    venue_data = {
        "name": "Test Concert Hall",
        "address": "123 Main Street",
        "city": "Berlin",
        "country": "Germany",
        "capacity": 2000,
    }
    
    response = await client.post("/venues", json=venue_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == venue_data["name"]
    assert data["address"] == venue_data["address"]
    assert data["city"] == venue_data["city"]
    assert data["country"] == venue_data["country"]
    assert data["capacity"] == venue_data["capacity"]
    assert "id" in data
    assert "created_at" in data
