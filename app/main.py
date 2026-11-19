
from fastapi import FastAPI

# Import models first
from app.models.user import User
from app.models.booking import Booking

# Import routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.bookings import router as bookings_router
from app.routers.admin import router as admin_router


app = FastAPI(
    title="Booking System API",
    version="1.0.0"
)


# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(bookings_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {
        "message": "Booking System API is running"
    }
