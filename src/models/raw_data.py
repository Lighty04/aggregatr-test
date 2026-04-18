from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .database import Base
from .venue import Venue
from .event import Event

class RawData(Base):
    """
    Represents raw data ingested from an external source before being processed 
    into a structured Event or Venue record.
    """
    __tablename__ = "raw_data"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Source identifier (e.g., 'ticketmaster', 'facebook_events')
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Raw JSON/XML payload (store the original data)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Ingestion Timestamp
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Status of processing (e.g., 'pending', 'processed', 'failed')
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    
    # Optional: Link to the Event this data was used to create/update
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=True, index=True)
    
    # Optional: Link to the Venue this data was used to create/update
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=True, index=True)

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="raw_data")
    venue: Mapped["Venue"] = relationship(back_populates="raw_data")

    # Define a composite index for quick lookups (e.g., all pending data from a specific source)
    __table_args__ = (
        Index('idx_raw_source_status', 'source', 'status'),
    )

    def __repr__(self) -> str:
        return f"RawData(id={self.id}, source='{self.source}', status='{self.status}')"