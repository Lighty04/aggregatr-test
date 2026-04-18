#!/usr/bin/env python3
"""
Populate database with events from fetchers.
Run this to fetch events and store them in the database.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, '/home/decisionhelper/aggregatr-test')

from src.models.database import create_db_and_tables, AsyncSessionLocal
from src.models.venue import Venue
from src.models.event import Event
from src.fetchers.runner import run_fetcher

async def populate():
    """Fetch events and populate database."""
    print("Setting up database...")
    await create_db_and_tables()
    
    print("Fetching events from Philharmonie...")
    result = await run_fetcher('philharmonie')
    
    if result['status'] != 'success':
        print(f"Fetch failed: {result.get('error', 'Unknown error')}")
        return
    
    events_data = result.get('events', [])
    print(f"Fetched {len(events_data)} events")
    
    if not events_data:
        print("No events to add")
        return
    
    async with AsyncSessionLocal() as db:
        # Create venue if doesn't exist
        venue = await db.get(Venue, 1)
        if not venue:
            venue = Venue(
                id=1,
                name="Philharmonie de Paris",
                url="https://www.philharmonie.fr",
                city="Paris",
                country="France"
            )
            db.add(venue)
            await db.commit()
            print("Created venue: Philharmonie de Paris")
        
        # Add events
        for event_data in events_data:
            event = Event(
                name=event_data.get('title', 'Unknown Event'),
                description=f"Date: {event_data.get('date_time', 'TBD')}",
                url=event_data.get('url', ''),
                venue_id=1,
                status='active'
            )
            db.add(event)
        
        await db.commit()
        print(f"Added {len(events_data)} events to database")

if __name__ == "__main__":
    asyncio.run(populate())
