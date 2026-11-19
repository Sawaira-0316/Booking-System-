
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# Booking Status Enum
class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


# 1. Create Booking Schema
class BookingCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    notes: str | None = None
    booking_date: datetime


# 2. Update Booking Schema
class BookingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    notes: str | None = None
    booking_date: datetime | None = None
    status: str | None = None


# 3. Booking Response Schema
class BookingResponse(BaseModel):
    id: int
    user_id: int
    title: str
    notes: str | None
    booking_date: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
