
import jwt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.user import User

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh
)
from app.schemas.user import UserResponse

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# REGISTER USER
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    existing_user = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return new_user


# LOGIN USER
@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()

    if not user or not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# REFRESH ACCESS TOKEN
@router.post("/refresh")
def refresh_access_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    try:
        # Verify refresh token
        payload = verify_token(
            token_data.refresh_token,
            expected_type="refresh"
        )

        # Extract user ID
        user_id = int(payload.get("sub"))

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Find user in database
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new access token
    new_access_token = create_access_token(user.id)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
