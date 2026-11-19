
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingStatus
)
from app.schemas.pagination import Page
from app.db.session import get_db
from app.models.user import User
from app.models.booking import Booking
from app.dependencies import get_current_user, PaginationParams


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


# Create booking
@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_booking = Booking(
        user_id=current_user.id,
        title=booking_data.title,
        notes=booking_data.notes,
        booking_date=booking_data.booking_date
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking


# Get bookings with pagination, total count and status filtering
@router.get("/", response_model=Page[BookingResponse])
def get_bookings(
    pagination: PaginationParams = Depends(),

    booking_status: BookingStatus | None = Query(
        default=None,
        alias="status"
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Base query
    query = select(Booking)

    # Count query
    count_query = select(func.count()).select_from(Booking)

    # Normal users can only see their own bookings
    if current_user.role != "admin":
        query = query.where(
            Booking.user_id == current_user.id
        )

        count_query = count_query.where(
            Booking.user_id == current_user.id
        )

    # Apply status filter if provided
    if booking_status is not None:
        query = query.where(
            Booking.status == booking_status.value
        )

        count_query = count_query.where(
            Booking.status == booking_status.value
        )

    # Calculate total matching bookings
    total = db.execute(count_query).scalar_one()

    # Apply stable ordering
    query = query.order_by(Booking.id.desc())

    # Apply pagination
    query = query.offset(pagination.skip).limit(pagination.limit)

    # Fetch current page bookings
    bookings = db.execute(query).scalars().all()

    # Check whether more records are available
    has_more = pagination.skip + len(bookings) < total

    return {
        "items": bookings,
        "total": total,
        "skip": pagination.skip,
        "limit": pagination.limit,
        "has_more": has_more
    }


# Get one booking
@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if (
        current_user.role != "admin"
        and booking.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another user's booking"
        )

    return booking


# Update booking
@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if (
        current_user.role != "admin"
        and booking.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot update another user's booking"
        )

    update_data = booking_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(booking, field, value)

    db.commit()
    db.refresh(booking)

    return booking


# Delete booking
@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.get(Booking, booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if (
        current_user.role != "admin"
        and booking.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete another user's booking"
        )

    db.delete(booking)
    db.commit()

    return {"message": "Booking deleted successfully"}
