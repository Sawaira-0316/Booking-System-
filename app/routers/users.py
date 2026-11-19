
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.dependencies import get_current_user, get_admin_user

from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    users = db.execute(
        select(User)
    ).scalars().all()

    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Update full name
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name

    # Check email uniqueness
    if user_data.email is not None:
        existing_user = db.execute(
            select(User).where(
                User.email == user_data.email,
                User.id != current_user.id
            )
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        current_user.email = user_data.email

    db.commit()
    db.refresh(current_user)

    return current_user