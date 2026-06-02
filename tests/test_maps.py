from app.maps import DEFAULT_MAPS, is_point_inside_map
from app.schemas import Point


def test_get_known_map():
    assert any(map_definition.map_id == "small_loop" for map_definition in DEFAULT_MAPS)


def test_point_inside_map():
    assert is_point_inside_map(Point(x=10, y=20), width=300, height=200)


def test_point_outside_map():
    assert not is_point_inside_map(Point(x=-1, y=20), width=300, height=200)
