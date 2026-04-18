"""Venues API router."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db_session
from src.models.venue import Venue
from src.models.event import Event


router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("")
async def list_venues(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
):
    """List venues with pagination."""
    query = select(Venue).offset(offset).limit(limit)
    result = await db.execute(query)
    venues = result.scalars().all()
    
    return {
        "items": [{
            "id": v.id,
            "name": v.name,
            "address": v.address,
            "city": v.city,
            "country": v.country,
            "capacity": v.capacity,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        } for v in venues],
        "limit": limit,
        "offset": offset,
    }


@router.get("/{venue_id}")
async def get_venue(
    venue_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a single venue by ID."""
    query = select(Venue).where(Venue.id == venue_id)
    result = await db.execute(query)
    venue = result.scalar_one_or_none()
    
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    return {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "country": venue.country,
        "capacity": venue.capacity,
        "created_at": venue.created_at.isoformat() if venue.created_at else None,
    }


@router.get("/{venue_id}/events")
async def get_venue_events(
    venue_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all events for a specific venue."""
    # First check if venue exists
    venue_query = select(Venue).where(Venue.id == venue_id)
    venue_result = await db.execute(venue_query)
    venue = venue_result.scalar_one_or_none()
    
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Get events for this venue
    events_query = (
        select(Event)
        .options(selectinload(Event.venue))
        .where(Event.venue_id == venue_id)
        .offset(offset)
        .limit(limit)
    )
    events_result = await db.execute(events_query)
    events = events_result.scalars().all()
    
    return {
        "venue_id": venue_id,
        "venue_name": venue.name,
        "items": [{
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "start_time": e.start_time.isoformat() if e.start_time else None,
            "end_time": e.end_time.isoformat() if e.end_time else None,
            "type": e.type.value if e.type else None,
            "status": e.status,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        } for e in events],
        "limit": limit,
        "offset": offset,
    }
