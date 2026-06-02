from collections import defaultdict, deque
from time import monotonic

from fastapi import Depends, HTTPException, Request, status

from app.config import Settings, get_settings


_request_buckets: dict[str, deque[float]] = defaultdict(deque)


def _client_id(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client is None:
        return "unknown"
    return request.client.host


def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    now = monotonic()
    bucket = _request_buckets[key]

    while bucket and now - bucket[0] >= window_seconds:
        bucket.popleft()

    if len(bucket) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Try again later.",
        )

    bucket.append(now)


def rate_limit_general(request: Request, settings: Settings = Depends(get_settings)) -> None:
    key = f"general:{_client_id(request)}"
    _check_rate_limit(key, settings.rate_limit_general_requests, settings.rate_limit_window_seconds)


def rate_limit_auth(request: Request, settings: Settings = Depends(get_settings)) -> None:
    key = f"auth:{_client_id(request)}"
    _check_rate_limit(key, settings.rate_limit_auth_requests, settings.rate_limit_window_seconds)


def clear_rate_limits() -> None:
    _request_buckets.clear()

