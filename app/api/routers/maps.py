from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import MapCatalog, MapCreate, MapDefinition
from app.security import get_current_user
from app.services import create_map, get_map, list_maps, to_map_definition


router = APIRouter(prefix="/maps", tags=["maps"])


@router.get("", response_model=MapCatalog)
def api_list_maps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MapCatalog:
    return list_maps(db, current_user.id)


@router.get("/{map_id}", response_model=MapDefinition)
def api_get_map(
    map_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MapDefinition:
    map_model = get_map(db, current_user.id, map_id)
    if map_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    return to_map_definition(map_model)


@router.post("", response_model=MapDefinition, status_code=status.HTTP_201_CREATED)
def api_create_map(
    map_data: MapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MapDefinition:
    try:
        map_model = create_map(db, current_user.id, map_data)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Map already exists") from exc
    return to_map_definition(map_model)
