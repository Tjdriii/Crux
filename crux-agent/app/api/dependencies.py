"""
Dependency injection for FastAPI endpoints.
"""
import uuid
from typing import Annotated, Optional

import redis.asyncio as redis
from celery import Celery
from fastapi import HTTPException, Request, status
import os

from app.core.providers.factory import create_provider
from app.core.providers.base import BaseProvider
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Global instances (initialized in lifespan)
redis_client: Optional[redis.Redis] = None
celery_app: Optional[Celery] = None


async def get_redis() -> Optional[redis.Redis]:
    """Get Redis client."""
    if not redis_client:
        return None
    return redis_client


async def get_celery() -> Optional[Celery]:
    """Get Celery app."""
    if not celery_app:
        return None
    return celery_app


async def get_request_id(
    request: Request,
) -> str:
    """Get or generate request ID."""
    # Check if already set in request state
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    
    # Generate new ID
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    request.state.request_id = request_id
    return request_id


async def get_provider(
    provider_name: Optional[str] = None,
) -> Optional[BaseProvider]:
    """
    Get LLM provider instance.
    
    Args:
        provider_name: Optional provider override
        
    Returns:
        Provider instance
    """
    try:
        return create_provider(provider_name=provider_name)
    except Exception as e:
        logger.error(f"Failed to create provider: {e}")
        return None


async def verify_api_key(request: Request) -> None:
    """Basic API key verification."""
    expected_key = os.getenv("API_KEY")
    if expected_key:
        api_key = request.headers.get("X-API-Key")
        if api_key != expected_key:
            logger.warning("Invalid API key provided")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


async def get_current_user_from_api_key(request: Request) -> dict:
    """Return a stub user derived from API key."""
    api_key = request.headers.get("X-API-Key", "anonymous")
    return {"id": api_key}


async def rate_limiter_standard() -> None:
    """Placeholder rate limiter that currently allows all requests."""
    return None
