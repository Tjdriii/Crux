import pytest
from fastapi import Request, HTTPException

from app.api import dependencies


def make_request(api_key: str | None = None) -> Request:
    headers = []
    if api_key is not None:
        headers.append((b"x-api-key", api_key.encode()))
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": headers,
        "client": ("test", 1234),
    }
    return Request(scope, receive=lambda: None)


@pytest.mark.asyncio
async def test_verify_api_key_success():
    req = make_request("valid-key")
    await dependencies.verify_api_key(req)
    assert req.state.api_key == "valid-key"
    user = await dependencies.get_current_user_from_api_key(req)
    assert user["id"] == "user-1"


@pytest.mark.asyncio
async def test_verify_api_key_failure():
    req = make_request("bad-key")
    with pytest.raises(HTTPException):
        await dependencies.verify_api_key(req)


@pytest.mark.asyncio
async def test_rate_limiter_standard():
    dependencies._rate_counter.clear()
    req = make_request("valid-key")
    req.state.api_key = "valid-key"
    for _ in range(dependencies._RATE_LIMIT):
        await dependencies.rate_limiter_standard(req)
    with pytest.raises(HTTPException):
        await dependencies.rate_limiter_standard(req)
