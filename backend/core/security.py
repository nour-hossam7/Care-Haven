from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.user import User


# =========================================================
# JWT Configuration
# =========================================================

ALGORITHM = "HS256"

oauth2_scheme = HTTPBearer()


# =========================================================
# Password Hashing
# =========================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plain-text password against its hash."""
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# =========================================================
# JWT Creation
# =========================================================

def create_access_token(
    user_id: str,
    role: str,
) -> str:
    """Create a JWT access token for an authenticated user."""

    expires_delta = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    expire = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


# =========================================================
# JWT Validation / Decoding
# =========================================================

def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# =========================================================
# Database Dependency
# =========================================================

def get_db():
    """Provide a database session for FastAPI dependencies."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# Current Authenticated User
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Return the currently authenticated user."""

    payload = decode_access_token(credentials.credentials)

    user_id = payload["sub"]

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# =========================================================
# Role-Based Authorization
# =========================================================

def require_role(*allowed_roles: str):
    """
    Create a dependency that allows only the specified roles.

    Example:
        Depends(require_role("admin"))
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        current_role = current_user.role.value

        if current_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker


# =========================================================
# Admin Authorization
# =========================================================

def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require the authenticated user to have the admin role."""

    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user