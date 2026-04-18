from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .database import Base

class Venue(Base):
    """
    Represents a physical venue where an event takes place.
    """
    __tablename__ = "venues"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Venue Name (should be unique)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Location/Address
    address: Mapped[str] = mapped_column(String(512), nullable=True)
    
    # City
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Country
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Capacity
    capacity: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Created At timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationship: A Venue can have many Events
    events: Mapped[list["Event"]] = relationship(back_populates="venue")

    # Define a composite index if needed, e.g., on (city, country)
    __table_args__ = (
        Index('idx_venue_location', 'city', 'country'),
    )

    def __repr__(self) -> str:
        return f"Venue(id={self.id}, name='{self.name}', city='{self.city}')"