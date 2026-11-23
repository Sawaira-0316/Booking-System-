
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingStatus
)
from app.schemas.pagination import Page, CursorPage
from app.db.session import get_db
from app.models.user import User
from app.models.booking import Booking
from app.dependencies import get_current_user, PaginationParams


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


# Shared filters used by both /bookings and /bookings/feed
def apply_booking_filters(
    query,
    current_user: User,
    booking_status: BookingStatus | None,
    from_date: date | None,
    to_date: date | None,
    search: str | None
):
    # Normal users can only see their own bookings
    if current_user.role != "admin":
        query = query.where(Booking.user_id == current_user.id)

    # Apply status filter
    if booking_status is not None:
        query = query.where(Booking.status == booking_status.value)

    # Apply starting date filter
    if from_date is not None:
        query = query.where(Booking.booking_date >= from_date)

    # Apply ending date filter
    if to_date is not None:
        query = query.where(
            Booking.booking_date < to_date + timedelta(days=1)
        )

    # Apply title search
    if search is not None:
        query = query.where(Booking.title.ilike(f"%{search}%"))

    return query


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


# Get bookings with pagination, filters, search and sorting
@router.get("/", response_model=Page[BookingResponse])
def get_bookings(
    pagination: PaginationParams = Depends(),

    booking_status: BookingStatus | None = Query(
        default=None,
        alias="status"
    ),

    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),

    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100
    ),

    # Sorting parameters
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc"),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Base query with all filters applied
    query = apply_booking_filters(
        select(Booking),
        current_user,
        booking_status,
        from_date,
        to_date,
        search
    )

    # Count query with the same filters
    count_query = apply_booking_filters(
        select(func.count()).select_from(Booking),
        current_user,
        booking_status,
        from_date,
        to_date,
        search
    )

    # Calculate total matching bookings
    total = db.execute(count_query).scalar_one()

    # Allowed sorting fields (whitelist)
    allowed_sort_fields = {
        "created_at": Booking.created_at,
        "booking_date": Booking.booking_date,
        "status": Booking.status
    }

    # Validate sort_by
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sorting field"
        )

    # Validate order
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be asc or desc"
        )

    # Get selected sorting column
    sort_column = allowed_sort_fields[sort_by]

    # Apply sorting with stable ID ordering
    if order == "asc":
        query = query.order_by(
            sort_column.asc(),
            Booking.id.asc()
        )
    else:
        query = query.order_by(
            sort_column.desc(),
            Booking.id.desc()
        )

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


# Cursor feed (keyset pagination)
# IMPORTANT: this route must stay ABOVE "/{booking_id}"
@router.get("/feed", response_model=CursorPage[BookingResponse])
def get_bookings_feed(
    # Bookmark: id of the last booking the client already received
    cursor: int | None = Query(default=None, ge=1),

    limit: int = Query(default=10, ge=1, le=100),

    # Same filters as /bookings
    booking_status: BookingStatus | None = Query(
        default=None,
        alias="status"
    ),

    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),

    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ownership rule and filters first
    query = apply_booking_filters(
        select(Booking),
        current_user,
        booking_status,
        from_date,
        to_date,
        search
    )

    # Only rows after the bookmark (newest first means smaller ids)
    if cursor is not None:
        query = query.where(Booking.id < cursor)

    # Newest first; ask for one extra row to know if more exist
    query = query.order_by(Booking.id.desc()).limit(limit + 1)

    rows = db.execute(query).scalars().all()

    # If the extra row came back, another page exists
    has_more = len(rows) > limit

    # Remove the extra row before returning
    items = rows[:limit]

    # Bookmark for the next page (None on the last page)
    next_cursor = items[-1].id if has_more else None

    return {
        "items": items,
        "limit": limit,
        "next_cursor": next_cursor,
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
