from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
from .venue import Venue
from .event import Event, EventType
from .raw_data import RawData

# --- Shared Base Schema ---
class BaseSchema(BaseModel):
    """Base schema for all models, including common fields."""
    id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- Venue Schemas ---
class VenueBaseSchema(BaseSchema):
    """Base schema for Venue (data required for creation/update)."""
    name: str = Field(..., description="Unique name of the venue.")
    address: Optional[str] = Field(None, description="Full street address.")
    city: Optional[str] = Field(None, description="City of the venue.")
    country: Optional[str] = Field(None, description="Country of the venue.")
    capacity: Optional[int] = Field(None, description="Maximum capacity of the venue.")

class VenueCreateSchema(VenueBaseSchema):
    """Schema used when creating a new Venue."""
    pass

class VenueUpdateSchema(VenueBaseSchema):
    """Schema used when updating an existing Venue (all fields optional)."""
    name: Optional[str] = Field(None, description="Unique name of the venue.")
    address: Optional[str] = Field(None, description="Full street address.")
    city: Optional[str] = Field(None, description="City of the venue.")
    country: Optional[str] = Field(None, description="Country of the venue.")
    capacity: Optional[int] = Field(None, description="Maximum capacity of the venue.")

class VenueReadSchema(VenueBaseSchema):
    """Schema used when reading/retrieving a Venue (includes all fields)."""
    # Relationships (optional, for nested output)
    events: Optional[list["EventReadSchema"]] = None
    raw_data: Optional[list["RawDataReadSchema"]] = None

    class Config:
        from_attributes = True # Allows Pydantic to read ORM attributes

# --- Event Schemas ---
class EventBaseSchema(BaseSchema):
    """Base schema for Event (data required for creation/update)."""
    name: str = Field(..., description="Name of the event.")
    description: Optional[str] = Field(None, description="Detailed description of the event.")
    start_time: datetime = Field(..., description="Start date and time of the event.")
    end_time: Optional[datetime] = Field(None, description="End date and time of the event.")
    type: EventType = Field(..., description="Type of the event (e.g., concert, sport).")
    venue_id: int = Field(..., description="ID of the associated venue.")
    status: str = Field(..., description="Current status of the event (e.g., upcoming, past).")

class EventCreateSchema(EventBaseSchema):
    """Schema used when creating a new Event."""
    pass

class EventUpdateSchema(EventBaseSchema):
    """Schema used when updating an existing Event (all fields optional)."""
    name: Optional[str] = Field(None, description="Name of the event.")
    description: Optional[str] = Field(None, description="Detailed description of the event.")
    start_time: Optional[datetime] = Field(None, description="Start date and time of the event.")
    end_time: Optional[datetime] = Field(None, description="End date and time of the event.")
    type: Optional[EventType] = Field(None, description="Type of the event.")
    venue_id: Optional[int] = Field(None, description="ID of the associated venue.")
    status: Optional[str] = Field(None, description="Current status of the event.")

class EventReadSchema(EventBaseSchema):
    """Schema used when reading/retrieving an Event (includes all fields)."""
    # Relationships
    venue: VenueReadSchema
    raw_data: Optional[list["RawDataReadSchema"]] = None

    class Config:
        from_attributes = True

# --- RawData Schemas ---
class RawDataBaseSchema(BaseSchema):
    """Base schema for RawData (data required for creation/update)."""
    source: str = Field(..., description="The external source of the data (e.g., 'ticketmaster').")
    payload: str = Field(..., description="The raw data payload (JSON/XML string).")
    status: str = Field(..., description="Processing status (e.g., pending, processed).")
    event_id: Optional[int] = Field(None, description="Optional ID of the linked Event.")
    venue_id: Optional[int] = Field(None, description="Optional ID of the linked Venue.")

class RawDataCreateSchema(RawDataBaseSchema):
    """Schema used when creating a new RawData entry."""
    pass

class RawDataUpdateSchema(RawDataBaseSchema):
    """Schema used when updating an existing RawData entry (all fields optional)."""
    source: Optional[str] = Field(None, description="The external source of the data.")
    payload: Optional[str] = Field(None, description="The raw data payload.")
    status: Optional[str] = Field(None, description="Processing status.")
    event_id: Optional[int] = Field(None, description="Optional ID of the linked Event.")
    venue_id: Optional[int] = Field(None, description="Optional ID of the linked Venue.")

class RawDataReadSchema(RawDataBaseSchema):
    """Schema used when reading/retrieving a RawData entry (includes all fields)."""
    # Relationships
    event: Optional[EventReadSchema] = None
    venue: Optional[VenueReadSchema] = None

    class Config:
        from_attributes = True