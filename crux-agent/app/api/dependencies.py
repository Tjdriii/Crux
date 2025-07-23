"""
Dependency injection for FastAPI endpoints.
"""
import uuid
from typing import Annotated, Optional

import redis.asyncio as redis
from celery import Celery
from fastapi import Request

from app.core.providers.factory import create_provider
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Global instances (initialized in lifespan)
redis_client: Optional[redis.Redis] = None
celery_app: Optional[Celery] = None


async def get_redis() -> redis.Redis:
    """Get Redis client."""
    if not redis_client:
        raise RuntimeError("Redis client not initialized")
    return redis_client


async def get_celery() -> Celery:
    """Get Celery app."""
    if not celery_app:
        raise RuntimeError("Celery app not initialized")
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
):
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
        raise


# ---------------------------------------------------------------------------
# API key verification and user lookup
# ---------------------------------------------------------------------------

# In a real application these would likely be stored in a database or
# environment variable.  For the purposes of this project we keep a simple
# in-memory mapping of API keys to user information.
_API_KEY_DB = {
    "valid-key": {"id": "user-1", "name": "Test User"},
}


async def verify_api_key(request: Request) -> None:
    """Validate that the request contains a valid API key."""

    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in _API_KEY_DB:
        logger.warning("Invalid or missing API key")
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # store for downstream dependencies
    request.state.api_key = api_key


async def get_current_user_from_api_key(request: Request) -> dict:
    """Return minimal user information extracted from the API key."""

    api_key = getattr(request.state, "api_key", None)
    user = _API_KEY_DB.get(api_key)
    return user or {"id": "anonymous"}


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

import time
from collections import defaultdict
from fastapi import HTTPException, status

_RATE_LIMIT = 5  # requests per minute per API key
_rate_counter: defaultdict[tuple[str, int], int] = defaultdict(int)


async def rate_limiter_standard(request: Request) -> None:
    """Simple in-memory rate limiter."""

    api_key = getattr(request.state, "api_key", request.client.host)
    now = int(time.time() / 60)  # minute window
    key = (api_key, now)
    _rate_counter[key] += 1
    if _rate_counter[key] > _RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for {api_key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )


__all__ = [
    "get_redis",
    "get_celery",
    "get_request_id",
    "get_provider",
    "verify_api_key",
    "get_current_user_from_api_key",
    "rate_limiter_standard",
]