from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Point(BaseModel):
    x: float
    y: float
    heading: float | None = Field(default=None, ge=0, lt=360)


class RouteCreate(BaseModel):
    map_id: str
    start: Point
    end: Point


class RouteRead(BaseModel):
    id: int
    map_id: str
    start: Point
    end: Point
    created_at: datetime
    is_current: bool

    model_config = ConfigDict(from_attributes=True)
