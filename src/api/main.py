from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.config import settings
from src.api.deps import get_db_session
from src.api import events, venues


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

app.include_router(events.router, prefix=settings.api_prefix)
app.include_router(venues.router, prefix=settings.api_prefix)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.api_version}
