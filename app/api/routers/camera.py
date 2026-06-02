from collections.abc import AsyncIterator

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.security import bearer_scheme, decode_access_token


router = APIRouter(prefix="/camera", tags=["camera"])


async def iter_camera_stream(camera_url: str) -> AsyncIterator[bytes]:
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", camera_url) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                yield chunk


def authorize_camera_stream(
    access_token: str | None = Query(default=None),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> None:
    token = credentials.credentials if credentials is not None else access_token
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    decode_access_token(token, settings)


@router.get("/stream", dependencies=[Depends(authorize_camera_stream)])
async def api_camera_stream(settings: Settings = Depends(get_settings)) -> StreamingResponse:
    try:
        return StreamingResponse(
            iter_camera_stream(settings.camera_stream_url),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )
    except httpx.HTTPError as exc:
        return Response(
            content=f"Camera stream unavailable: {exc}",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )
