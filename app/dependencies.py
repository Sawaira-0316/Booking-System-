from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.auth.security import verify_token


# Extract Bearer token from Authorization header
bearer_scheme = HTTPBearer()


# Reusable pagination dependency
class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
    ):
        self.skip = skip
        self.limit = limit


# Get currently authenticated user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        # Extract token string
        token = credentials.credentials

        # Verify access token
        payload = verify_token(token, expected_type="access")

        # Get user ID from token
        user_id = int(payload.get("sub"))

        if user_id <= 0:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Find user in database
    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    # Check whether account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


# Check whether current user is admin
def get_admin_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user