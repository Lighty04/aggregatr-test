#!/usr/bin/env python3
"""
Populate database with mock events for testing.
"""

import asyncio
import sys
import os

sys.path.insert(0, '/home/decisionhelper/aggregatr-test')

from src.models.database import create_db_and_tables, AsyncSessionLocal
from src.models.venue import Venue
from src.models.event import Event

async def populate_mock():
    print("Setting up database...")
    await create_db_and_tables()
    
    async with AsyncSessionLocal() as db:
        # Create venue
        venue = Venue(
            id=1,
            name="Philharmonie de Paris",
            address="221 Avenue Jean Jaurès, 75019 Paris",
            city="Paris",
            country="France"
        )
        db.add(venue)
        await db.commit()
        print("Created venue: Philharmonie de Paris")
        
        # Add mock events
        events = [
            {"name": "Concert Symphonique", "desc": "Beethoven Symphony No. 9"},
            {"name": "Recital Piano", "desc": "Chopin Nocturnes"},
            {"name": "Orchestre National", "desc": "Ravel Bolero"},
            {"name": "Quatuor Debussy", "desc": "String Quartet Performance"},
            {"name": "Jazz Festival", "desc": "Evening of Contemporary Jazz"},
        ]
        
        for i, e in enumerate(events, 1):
            event = Event(
                id=i,
                name=e["name"],
                description=e["desc"],
                venue_id=1,
                status="active"
            )
            db.add(event)
        
        await db.commit()
        print(f"Added {len(events)} mock events to database")

if __name__ == "__main__":
    asyncio.run(populate_mock())
