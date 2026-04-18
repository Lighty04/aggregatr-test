"""Full integration tests for the event aggregator flow."""

import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_full_flow(client, async_session):
    """Test the full flow: create venue -> create event -> fetch via API."""
    # Step 1: Create a venue via API
    venue_data = {
        "name": "Philharmonie Luxembourg",
        "address": "1 Place de l'Europe",
        "city": "Luxembourg",
        "country": "Luxembourg",
        "capacity": 1500,
    }
    
    venue_response = await client.post("/venues", json=venue_data)
    assert venue_response.status_code == 200
    
    created_venue = venue_response.json()
    venue_id = created_venue["id"]
    assert venue_id is not None
    assert created_venue["name"] == venue_data["name"]
    
    # Step 2: Create an event via API associated with the venue
    start_time = (datetime.utcnow() + timedelta(days=14)).isoformat()
    end_time = (datetime.utcnow() + timedelta(days=14, hours=2)).isoformat()
    
    event_data = {
        "name": "Classical Symphony Night",
        "description": "An evening with the Luxembourg Philharmonic",
        "start_time": start_time,
        "end_time": end_time,
        "type": "concert",
        "venue_id": venue_id,
        "status": "upcoming",
    }
    
    event_response = await client.post("/events", json=event_data)
    assert event_response.status_code == 200
    
    created_event = event_response.json()
    event_id = created_event["id"]
    assert event_id is not None
    assert created_event["name"] == event_data["name"]
    assert created_event["venue_id"] == venue_id
    
    # Step 3: Fetch venues via API and verify the created venue is included
    venues_response = await client.get("/venues")
    assert venues_response.status_code == 200
    venues = venues_response.json()
    assert isinstance(venues, list)
    assert len(venues) >= 1
    
    # Find our created venue
    matching_venues = [v for v in venues if v["id"] == venue_id]
    assert len(matching_venues) == 1
    fetched_venue = matching_venues[0]
    assert fetched_venue["name"] == venue_data["name"]
    assert fetched_venue["city"] == venue_data["city"]
    
    # Step 4: Fetch events via API and verify the created event is included
    events_response = await client.get("/events")
    assert events_response.status_code == 200
    events = events_response.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    
    # Find our created event
    matching_events = [e for e in events if e["id"] == event_id]
    assert len(matching_events) == 1
    fetched_event = matching_events[0]
    assert fetched_event["name"] == event_data["name"]
    assert fetched_event["venue_id"] == venue_id
    assert fetched_event["type"] == "concert"
    
    # Step 5: Fetch venue with events and verify relationship
    venue_events_response = await client.get(f"/venues/{venue_id}/events")
    assert venue_events_response.status_code == 200
    venue_with_events = venue_events_response.json()
    
    assert venue_with_events["venue"]["id"] == venue_id
    assert venue_with_events["venue"]["name"] == venue_data["name"]
    assert len(venue_with_events["events"]) >= 1
    
    # Verify our event is in the list
    event_names = [e["name"] for e in venue_with_events["events"]]
    assert event_data["name"] in event_names
