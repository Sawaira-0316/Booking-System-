
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking


class User(Base):
    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # User Full Name
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    # User Email
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Hashed Password
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User Role
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False
    )

    # Account Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Account Creation Time
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # One-to-Many Relationship with Booking
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user"
    )
