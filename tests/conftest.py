"""Pytest configuration and fixtures for integration tests."""

import asyncio
from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.models.base import Base
from src.models.venue import Venue
from src.models.event import Event, EventType

# Register pytest-asyncio plugin
pytest_plugins = ["pytest_asyncio"]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create an async engine with SQLite in-memory database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session() as session:
        yield session
        # Rollback and clean up after test
        await session.rollback()


@pytest_asyncio.fixture
async def client(async_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an HTTPX async client with FastAPI test app."""
    # Import here to avoid circular imports
    from fastapi import FastAPI, Depends, HTTPException
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from httpx import ASGITransport
    
    # Create test FastAPI app
    app = FastAPI(title="Test Aggregatr API")
    
    # Create async session maker bound to the test engine
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        """Dependency to get database session."""
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.close()
    
    # Health endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    # Get venues endpoint
    @app.get("/venues")
    async def get_venues(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Venue))
        venues = result.scalars().all()
        return [
            {
                "id": v.id,
                "name": v.name,
                "address": v.address,
                "city": v.city,
                "country": v.country,
                "capacity": v.capacity,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in venues
        ]
    
    # Get events endpoint
    @app.get("/events")
    async def get_events(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Event))
        events = result.scalars().all()
        return [
            {
                "id": e.id,
                "name": e.name,
                "description": e.description,
                "start_time": e.start_time.isoformat() if e.start_time else None,
                "end_time": e.end_time.isoformat() if e.end_time else None,
                "type": e.type.value if e.type else None,
                "venue_id": e.venue_id,
                "status": e.status,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ]
    
    # Create venue endpoint
    @app.post("/venues")
    async def create_venue(
        venue_data: dict,
        db: AsyncSession = Depends(get_db),
    ):
        venue = Venue(
            name=venue_data.get("name"),
            address=venue_data.get("address"),
            city=venue_data.get("city"),
            country=venue_data.get("country"),
            capacity=venue_data.get("capacity"),
        )
        db.add(venue)
        await db.commit()
        await db.refresh(venue)
        return {
            "id": venue.id,
            "name": venue.name,
            "address": venue.address,
            "city": venue.city,
            "country": venue.country,
            "capacity": venue.capacity,
            "created_at": venue.created_at.isoformat() if venue.created_at else None,
        }
    
    # Create event endpoint
    @app.post("/events")
    async def create_event(
        event_data: dict,
        db: AsyncSession = Depends(get_db),
    ):
        event = Event(
            name=event_data.get("name"),
            description=event_data.get("description"),
            start_time=datetime.fromisoformat(event_data.get("start_time")),
            end_time=datetime.fromisoformat(event_data.get("end_time")) if event_data.get("end_time") else None,
            type=EventType(event_data.get("type", "other")),
            venue_id=event_data.get("venue_id"),
            status=event_data.get("status", "upcoming"),
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start_time": event.start_time.isoformat() if event.start_time else None,
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "type": event.type.value if event.type else None,
            "venue_id": event.venue_id,
            "status": event.status,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
    
    # Get venue with events endpoint
    @app.get("/venues/{venue_id}/events")
    async def get_venue_events(venue_id: int, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = result.scalar_one_or_none()
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        events_result = await db.execute(select(Event).where(Event.venue_id == venue_id))
        events = events_result.scalars().all()
        
        return {
            "venue": {
                "id": venue.id,
                "name": venue.name,
                "city": venue.city,
                "country": venue.country,
            },
            "events": [
                {
                    "id": e.id,
                    "name": e.name,
                    "start_time": e.start_time.isoformat() if e.start_time else None,
                    "status": e.status,
                }
                for e in events
            ],
        }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
