from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, func

# Define the Base class for declarative models
class Base(DeclarativeBase):
    """Base class which provides automated table name
    and declarative mapping to all models."""
    pass

# Database URL (using SQLite for simplicity, can be changed to PostgreSQL/MySQL)
# Example for PostgreSQL: "postgresql+asyncpg://user:password@host/dbname"
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./aggregatr_test.db"

# Create the async engine
# echo=True prints the generated SQL to the console
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True, 
    future=True
)

# Create a session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

# Dependency function to get a database session
async def get_db() -> AsyncSession:
    """
    Provides a database session for use in API endpoints.
    Ensures the session is closed after use.
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

# Function to create all tables in the database
async def create_db_and_tables():
    """
    Creates all tables defined by models inheriting from Base.
    """
    async with engine.begin() as conn:
        # Drop all tables first (optional, useful for development/testing)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

# Example usage (optional, but good practice)
async def main():
    print("Starting database setup...")
    await create_db_and_tables()
    print("Database and tables created successfully.")
    
    # Example of getting a session and using it
    async with AsyncSessionLocal() as db:
        # You can perform queries here
        print("Database session acquired successfully.")
        # Example: print(db.execute(select(Venue)).scalars().first())
        pass

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())