from datetime import datetime, timedelta, timezone
import random
import secrets
import uuid

from app.db.session import SessionLocal
from app.models.user import User
from app.models.booking import Booking
from app.auth.security import hash_password


# Configuration
TARGET_USERS = 50
TARGET_BOOKINGS = 100_000
BATCH_SIZE = 5_000


# Sample data
FIRST_NAMES = [
    "Ali", "Ahmed", "Sara", "Ayesha", "Fatima",
    "Usman", "Hassan", "Zain", "Mariam", "Sana",
    "Hamza", "Hira", "Bilal", "Amna", "Kashif"
]

LAST_NAMES = [
    "Khan", "Malik", "Ahmed", "Sheikh", "Asghar",
    "Raza", "Butt", "Iqbal", "Ali", "Siddiqui"
]

TITLES = [
    "Doctor Appointment",
    "Hotel Reservation",
    "Meeting Room",
    "Dental Checkup",
    "Flight Reservation",
    "Business Meeting",
    "Office Consultation",
    "Restaurant Booking",
    "Car Service",
    "Project Discussion"
]

STATUSES = ["pending", "confirmed", "cancelled"]

NOTES = [
    "Regular appointment",
    "Please confirm the booking",
    "Scheduled through online system",
    "Customer requested this time",
    "Sample booking for testing",
    "Follow-up required",
    "No additional instructions"
]


def random_datetime(start_date, end_date):
    """Generate a random timezone-aware datetime."""
    total_seconds = int((end_date - start_date).total_seconds())

    return start_date + timedelta(
        seconds=random.randint(0, total_seconds)
    )


def create_users(db):
    """Ensure at least 50 users exist."""

    existing_users = db.query(User).count()

    if existing_users >= TARGET_USERS:
        print(f"Already have {existing_users} users.")
        return

    users_to_create = TARGET_USERS - existing_users

    print(f"Creating {users_to_create} additional users...")

    # Random password is generated and hashed.
    # It is not printed or stored as plain text.
    seed_password_hash = hash_password(
        secrets.token_urlsafe(32)
    )

    new_users = []

    for _ in range(users_to_create):
        full_name = (
            f"{random.choice(FIRST_NAMES)} "
            f"{random.choice(LAST_NAMES)}"
        )

        email = f"seed_{uuid.uuid4().hex}@example.com"

        user = User(
            full_name=full_name,
            email=email,
            password_hash=seed_password_hash,
            role="user",
            is_active=True
        )

        new_users.append(user)

    db.add_all(new_users)
    db.commit()

    total_users = db.query(User).count()

    print(f"Users ready. Total users: {total_users}")


def create_bookings(db):
    """Generate bookings in batches."""

    current_count = db.query(Booking).count()

    if current_count >= TARGET_BOOKINGS:
        print(f"Already have {current_count} bookings.")
        return

    remaining = TARGET_BOOKINGS - current_count

    users = db.query(User.id).all()
    user_ids = [user_id for (user_id,) in users]

    if len(user_ids) < TARGET_USERS:
        raise ValueError(
            "At least 50 users are required before creating bookings."
        )

    print(f"Creating {remaining} bookings...")

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=730)

    created = 0

    while created < remaining:
        current_batch_size = min(
            BATCH_SIZE,
            remaining - created
        )

        batch = []

        for _ in range(current_batch_size):
            booking = Booking(
                user_id=random.choice(user_ids),
                title=random.choice(TITLES),
                notes=random.choice(NOTES),
                booking_date=random_datetime(
                    start_date,
                    end_date
                ),
                status=random.choice(STATUSES),
                created_at=random_datetime(
                    start_date,
                    end_date
                )
            )

            batch.append(booking)

        db.add_all(batch)
        db.commit()

        created += current_batch_size

        print(
            f"Inserted {created}/{remaining} new bookings"
        )

    total_bookings = db.query(Booking).count()

    print(f"Booking generation complete. Total: {total_bookings}")


def main():
    db = SessionLocal()

    try:
        print("Starting database seeding...")

        create_users(db)
        create_bookings(db)

        print("Seed process completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()