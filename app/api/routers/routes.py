from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.maps import is_point_inside_map
from app.models import User
from app.schemas import RouteCreate, RouteRead
from app.security import get_current_user
from app.services import create_route, get_current_route, get_map, to_route_read


router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def api_create_route(
    route_data: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RouteRead:
    map_model = get_map(db, current_user.id, route_data.map_id)
    if map_model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown map_id")
    if not is_point_inside_map(route_data.start, map_model.width, map_model.height):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start point is outside map")
    if not is_point_inside_map(route_data.end, map_model.width, map_model.height):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End point is outside map")

    route = create_route(db, current_user.id, route_data)
    return to_route_read(route)


@router.get("/current", response_model=RouteRead)
def api_get_current_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RouteRead:
    route = get_current_route(db, current_user.id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Current route not found")
    return to_route_read(route)
