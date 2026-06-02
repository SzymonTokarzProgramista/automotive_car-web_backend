from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HealthStatus


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
def health(db: Session = Depends(get_db)) -> HealthStatus:
    db.execute(text("SELECT 1"))
    return HealthStatus(status="ok", database="ok")

