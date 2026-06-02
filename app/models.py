from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    email_verification_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    email_verification_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    maps: Mapped[list["Map"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    routes: Mapped[list["Route"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Map(Base):
    __tablename__ = "maps"
    __table_args__ = (UniqueConstraint("owner_id", "map_id", name="uq_maps_owner_map_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    map_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    coordinate_unit: Mapped[str] = mapped_column(String(24), nullable=False, default="cm")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    owner: Mapped[User] = relationship(back_populates="maps")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    map_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    start_x: Mapped[float] = mapped_column(Float, nullable=False)
    start_y: Mapped[float] = mapped_column(Float, nullable=False)
    start_heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_x: Mapped[float] = mapped_column(Float, nullable=False)
    end_y: Mapped[float] = mapped_column(Float, nullable=False)
    end_heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    owner: Mapped[User] = relationship(back_populates="routes")
