from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base
from .venue import Venue

# Define possible event types
class EventType(PyEnum):
    CONCERT = "concert"
    SPORT = "sport"
    CONFERENCE = "conference"
    FESTIVAL = "festival"
    OTHER = "other"

class Event(Base):
    """
    Represents a single event.
    """
    __tablename__ = "events"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Event Name
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Description
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    
    # Start Time
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # End Time
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    
    # Event Type
    type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False, default=EventType.OTHER, index=True)
    
    # Venue Foreign Key
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=False, index=True)
    
    # Relationship: Link to the Venue
    venue: Mapped["Venue"] = relationship(back_populates="events")

    # Status (e.g., 'upcoming', 'ongoing', 'past', 'cancelled')
    status: Mapped[str] = mapped_column(String(50), default="upcoming", index=True)
    
    # Created At timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Define a composite index for quick lookups (e.g., events in a specific venue)
    __table_args__ = (
        Index('idx_event_venue_time', 'venue_id', 'start_time'),
    )

    def __repr__(self) -> str:
        return f"Event(id={self.id}, name='{self.name}', venue_id={self.venue_id})"