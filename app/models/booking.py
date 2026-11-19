
from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.db.base import Base
from app.models.user import User


class Booking(Base):
    __tablename__ = "bookings"

    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Foreign Key: Booking belongs to a User
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Booking Title
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Optional Booking Notes
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Booking Date and Time
    booking_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Booking Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    # Booking Creation Time
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship with User Model
    user: Mapped[User] = relationship(
        back_populates="bookings"
    )
