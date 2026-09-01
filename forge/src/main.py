from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup lifecycle
    yield
    # Shutdown lifecycle


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "devplanet-forge",
        "version": settings.version,
    }
