from app.schemas import MapCreate, Point


DEFAULT_MAPS: tuple[MapCreate, ...] = (
    MapCreate(
        map_id="small_loop",
        name="Small loop",
        description="Compact loop for basic autonomous driving tests.",
        width=300,
        height=200,
    ),
    MapCreate(
        map_id="crossroads",
        name="Crossroads",
        description="Intersection layout for route and turning scenarios.",
        width=400,
        height=400,
    ),
    MapCreate(
        map_id="parking",
        name="Parking",
        description="Parking area layout for precise maneuvers.",
        width=500,
        height=300,
    ),
)


def is_point_inside_map(point: Point, width: float, height: float) -> bool:
    return 0 <= point.x <= width and 0 <= point.y <= height
