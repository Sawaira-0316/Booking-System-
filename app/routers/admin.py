from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserRoleUpdate
from app.dependencies import get_admin_user


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    users = db.execute(
        select(User)
    ).scalars().all()

    return users




@router.patch("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = role_data.role

    db.commit()
    db.refresh(user)

    return user
