from fastapi import APIRouter, Depends

from app.api.routers import auth, camera, health, maps, routes
from app.rate_limit import rate_limit_general
from app.security import require_jwt_token


api_router = APIRouter(dependencies=[Depends(rate_limit_general)])
token_dependency = [Depends(require_jwt_token)]

api_router.include_router(auth.router)
api_router.include_router(health.router, dependencies=token_dependency)
api_router.include_router(maps.router, prefix="/api")
api_router.include_router(routes.router, prefix="/api")
api_router.include_router(camera.router, prefix="/api")
