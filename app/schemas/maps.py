from pydantic import BaseModel, Field


class MapCreate(BaseModel):
    map_id: str
    name: str
    description: str
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    coordinate_unit: str = "cm"


class MapDefinition(MapCreate):
    id: int


class MapCatalog(BaseModel):
    maps: tuple[MapDefinition, ...]
