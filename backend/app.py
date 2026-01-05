"""
Sports Prophet API - Main FastAPI Application.

This module initializes the FastAPI application with all routes and middleware.
"""
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.register_device import router as register_device_router
from backend.api.send_stream import router as send_stream_router
from backend.api.get_live_stats import router as get_live_stats_router
from backend.api.get_historical_stats import router as get_historical_stats_router
from backend.api.kafka_topics import router as kafka_topics_router
from backend.config import CORS_ORIGINS, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Sports Prophet API...")
    yield
    # Shutdown
    logger.info("Shutting down Sports Prophet API...")


# Initialize FastAPI application
app = FastAPI(
    title="Sports Prophet API",
    description="Real-time sports analytics platform using Kafka and Spark",
    version="1.0.0",
    lifespan=lifespan,
)

# =============================================================================
# CORS Middleware
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Route Registration
# =============================================================================

# Device management
app.include_router(
    register_device_router,
    tags=["Device Management"],
)

# Data streaming
app.include_router(
    send_stream_router,
    tags=["Data Streaming"],
)

# Live statistics
app.include_router(
    get_live_stats_router,
    tags=["Live Statistics"],
)

# Historical statistics
app.include_router(
    get_historical_stats_router,
    tags=["Historical Statistics"],
)

# Kafka topic management
app.include_router(
    kafka_topics_router,
    tags=["Kafka Topics"],
)


# =============================================================================
# Root Endpoint
# =============================================================================

@app.get("/", tags=["Health"])
def read_root() -> Dict[str, str]:
    """
    Root endpoint to check API health status.
    
    Returns:
        Dict with API status message
    """
    return {"message": "Sports Prophet API is running."}


@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for container orchestration.
    
    Returns:
        Dict with health status
    """
    return {"status": "healthy"}

