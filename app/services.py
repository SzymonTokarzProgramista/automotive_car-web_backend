from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.maps import DEFAULT_MAPS
from app.models import Map, Route, User
from app.schemas import MapCatalog, MapCreate, MapDefinition, Point, RouteCreate, RouteRead, UserRegister


def create_user(
    db: Session,
    user_data: UserRegister,
    password_hash: str,
    email_verified: bool,
    verification_token_hash: str | None,
    verification_expires_at,
) -> User:
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        email_verified=email_verified,
        email_verification_token_hash=verification_token_hash,
        email_verification_expires_at=verification_expires_at,
    )
    db.add(user)
    db.flush()

    for map_data in DEFAULT_MAPS:
        db.add(
            Map(
                owner_id=user.id,
                map_id=map_data.map_id,
                name=map_data.name,
                description=map_data.description,
                width=map_data.width,
                height=map_data.height,
                coordinate_unit=map_data.coordinate_unit,
            )
        )

    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_verification_token_hash(db: Session, token_hash: str) -> User | None:
    return db.scalars(select(User).where(User.email_verification_token_hash == token_hash)).first()


def verify_user_email(db: Session, user: User) -> User:
    user.email_verified = True
    user.email_verification_token_hash = None
    user.email_verification_expires_at = None
    db.commit()
    db.refresh(user)
    return user


def is_verification_token_expired(user: User) -> bool:
    if user.email_verification_expires_at is None:
        return True
    expires_at = user.email_verification_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at < datetime.now(UTC)


def create_map(db: Session, owner_id: int, map_data: MapCreate) -> Map:
    map_model = Map(
        owner_id=owner_id,
        map_id=map_data.map_id,
        name=map_data.name,
        description=map_data.description,
        width=map_data.width,
        height=map_data.height,
        coordinate_unit=map_data.coordinate_unit,
    )
    db.add(map_model)
    db.commit()
    db.refresh(map_model)
    return map_model


def get_map(db: Session, owner_id: int, map_id: str) -> Map | None:
    return db.scalars(select(Map).where(Map.owner_id == owner_id, Map.map_id == map_id)).first()


def list_maps(db: Session, owner_id: int) -> MapCatalog:
    maps = db.scalars(select(Map).where(Map.owner_id == owner_id).order_by(Map.id)).all()
    return MapCatalog(maps=tuple(to_map_definition(map_model) for map_model in maps))


def create_route(db: Session, owner_id: int, route_data: RouteCreate) -> Route:
    db.execute(update(Route).where(Route.owner_id == owner_id, Route.is_current.is_(True)).values(is_current=False))
    route = Route(
        owner_id=owner_id,
        map_id=route_data.map_id,
        start_x=route_data.start.x,
        start_y=route_data.start.y,
        start_heading=route_data.start.heading,
        end_x=route_data.end.x,
        end_y=route_data.end.y,
        end_heading=route_data.end.heading,
        is_current=True,
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


def get_current_route(db: Session, owner_id: int) -> Route | None:
    return db.scalars(
        select(Route)
        .where(Route.owner_id == owner_id, Route.is_current.is_(True))
        .order_by(Route.created_at.desc(), Route.id.desc())
    ).first()


def to_map_definition(map_model: Map) -> MapDefinition:
    return MapDefinition(
        id=map_model.id,
        map_id=map_model.map_id,
        name=map_model.name,
        description=map_model.description,
        width=map_model.width,
        height=map_model.height,
        coordinate_unit=map_model.coordinate_unit,
    )


def to_route_read(route: Route) -> RouteRead:
    return RouteRead(
        id=route.id,
        map_id=route.map_id,
        start=Point(x=route.start_x, y=route.start_y, heading=route.start_heading),
        end=Point(x=route.end_x, y=route.end_y, heading=route.end_heading),
        created_at=route.created_at,
        is_current=route.is_current,
    )
