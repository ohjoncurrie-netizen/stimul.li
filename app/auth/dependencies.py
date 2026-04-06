from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_api_key_value(request) -> str | None:
    return request.headers.get("X-API-Key")


def get_current_user(
    api_key: str | None = Security(api_key_header),
    db: Session = Depends(get_db),
) -> User:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key.",
        )

    user = db.scalar(select(User).where(User.api_key == api_key))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return user
