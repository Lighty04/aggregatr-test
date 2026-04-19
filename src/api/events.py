"""Events API router."""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db_session
from src.models.event import Event
from src.models.venue import Venue


router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
async def list_events(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    venue_id: Optional[int] = Query(default=None, description="Filter by venue ID"),
    start_date: Optional[datetime] = Query(default=None, description="Filter by start date (inclusive)"),
    end_date: Optional[datetime] = Query(default=None, description="Filter by end date (inclusive)"),
    db: AsyncSession = Depends(get_db_session),
):
    """List events with pagination and optional filters."""
    query = select(Event).options(selectinload(Event.venue))
    
    # Apply filters
    if venue_id is not None:
        query = query.where(Event.venue_id == venue_id)
    if start_date is not None:
        query = query.where(Event.start_time >= start_date)
    if end_date is not None:
        query = query.where(Event.start_time <= end_date)
    
    # Get total count for pagination
    count_query = select(func.count()).select_from(Event)
    if venue_id is not None:
        count_query = count_query.where(Event.venue_id == venue_id)
    if start_date is not None:
        count_query = count_query.where(Event.start_time >= start_date)
    if end_date is not None:
        count_query = count_query.where(Event.start_time <= end_date)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Add pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    total_pages = (total + limit - 1) // limit
    current_page = (offset // limit) + 1
    
    return {
        "items": [{
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "start_time": e.start_time.isoformat() if e.start_time else None,
            "end_time": e.end_time.isoformat() if e.end_time else None,
            "type": e.type.value if e.type else None,
            "venue_id": e.venue_id,
            "status": e.status,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "venue": {
                "id": e.venue.id,
                "name": e.venue.name,
                "city": e.venue.city,
                "country": e.venue.country,
            } if e.venue else None,
        } for e in events],
        "limit": limit,
        "offset": offset,
        "total": total,
        "total_pages": total_pages,
        "current_page": current_page,
    }


@router.get("/{event_id}")
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a single event by ID."""
    query = select(Event).options(selectinload(Event.venue)).where(Event.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
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
        "venue": {
            "id": event.venue.id,
            "name": event.venue.name,
            "address": event.venue.address,
            "city": event.venue.city,
            "country": event.venue.country,
            "capacity": event.venue.capacity,
        } if event.venue else None,
    }


@router.get("/search")
async def search_events(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
):
    """Search events by name or description."""
    search_pattern = f"%{q}%"
    query = (
        select(Event)
        .options(selectinload(Event.venue))
        .where(
            (Event.name.ilike(search_pattern)) | 
            (Event.description.ilike(search_pattern))
        )
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return {
        "items": [{
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "start_time": e.start_time.isoformat() if e.start_time else None,
            "end_time": e.end_time.isoformat() if e.end_time else None,
            "type": e.type.value if e.type else None,
            "venue_id": e.venue_id,
            "status": e.status,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "venue": {
                "id": e.venue.id,
                "name": e.venue.name,
                "city": e.venue.city,
                "country": e.venue.country,
            } if e.venue else None,
        } for e in events],
        "query": q,
        "limit": limit,
        "offset": offset,
    }


@router.post("")
async def create_event(
    event_data: dict,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new event."""
    from src.models.event import EventType
    
    # Parse event type if provided
    event_type = event_data.get("type", "other")
    if isinstance(event_type, str):
        try:
            event_type = EventType[event_type.upper()]
        except KeyError:
            event_type = EventType.OTHER
    
    # Parse dates
    start_time = event_data.get("start_time")
    end_time = event_data.get("end_time")
    
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    
    new_event = Event(
        name=event_data["name"],
        description=event_data.get("description"),
        start_time=start_time,
        end_time=end_time,
        type=event_type,
        venue_id=event_data["venue_id"],
        status=event_data.get("status", "upcoming"),
    )
    
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    
    # Load venue relationship
    query = select(Event).options(selectinload(Event.venue)).where(Event.id == new_event.id)
    result = await db.execute(query)
    event = result.scalar_one()
    
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
        "venue": {
            "id": event.venue.id,
            "name": event.venue.name,
            "city": event.venue.city,
            "country": event.venue.country,
        } if event.venue else None,
    }
