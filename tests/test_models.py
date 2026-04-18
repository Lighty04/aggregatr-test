"""Database model tests."""

import pytest
from datetime import datetime, timedelta

from src.models.venue import Venue
from src.models.event import Event, EventType


@pytest.mark.asyncio
async def test_create_venue(async_session):
    """Test creating a venue in the database."""
    venue = Venue(
        name="Test Venue",
        address="456 Oak Street",
        city="Vienna",
        country="Austria",
        capacity=1500,
    )
    
    async_session.add(venue)
    await async_session.commit()
    await async_session.refresh(venue)
    
    assert venue.id is not None
    assert venue.name == "Test Venue"
    assert venue.city == "Vienna"
    assert venue.capacity == 1500
    assert venue.created_at is not None


@pytest.mark.asyncio
async def test_create_event(async_session):
    """Test creating an event in the database."""
    # First create a venue
    venue = Venue(
        name="Event Venue",
        address="789 Pine Avenue",
        city="Paris",
        country="France",
        capacity=3000,
    )
    async_session.add(venue)
    await async_session.commit()
    await async_session.refresh(venue)
    
    # Create an event associated with the venue
    start_time = datetime.utcnow() + timedelta(days=7)
    end_time = start_time + timedelta(hours=3)
    
    event = Event(
        name="Jazz Concert",
        description="An evening of smooth jazz",
        start_time=start_time,
        end_time=end_time,
        type=EventType.CONCERT,
        venue_id=venue.id,
        status="upcoming",
    )
    
    async_session.add(event)
    await async_session.commit()
    await async_session.refresh(event)
    
    assert event.id is not None
    assert event.name == "Jazz Concert"
    assert event.type == EventType.CONCERT
    assert event.venue_id == venue.id
    assert event.start_time == start_time
    assert event.end_time == end_time


@pytest.mark.asyncio
async def test_venue_event_relationship(async_session):
    """Test the relationship between Venue and Event."""
    # Create a venue with events
    venue = Venue(
        name="Multi-Event Venue",
        address="101 Concert Blvd",
        city="London",
        country="UK",
        capacity=5000,
    )
    async_session.add(venue)
    await async_session.commit()
    await async_session.refresh(venue)
    
    # Create multiple events for this venue
    start_time1 = datetime.utcnow() + timedelta(days=10)
    event1 = Event(
        name="Rock Festival",
        description="A day of rock music",
        start_time=start_time1,
        end_time=start_time1 + timedelta(hours=5),
        type=EventType.FESTIVAL,
        venue_id=venue.id,
        status="upcoming",
    )
    
    start_time2 = datetime.utcnow() + timedelta(days=15)
    event2 = Event(
        name="Tech Conference",
        description="Annual tech summit",
        start_time=start_time2,
        end_time=start_time2 + timedelta(hours=8),
        type=EventType.CONFERENCE,
        venue_id=venue.id,
        status="upcoming",
    )
    
    async_session.add(event1)
    async_session.add(event2)
    await async_session.commit()
    
    # Refresh venue to load relationships
    await async_session.refresh(venue)
    
    # Check that venue has events relationship
    assert len(venue.events) == 2
    event_names = {e.name for e in venue.events}
    assert "Rock Festival" in event_names
    assert "Tech Conference" in event_names
    
    # Check that events have venue relationship
    for event in venue.events:
        assert event.venue.id == venue.id
        assert event.venue.name == "Multi-Event Venue"
