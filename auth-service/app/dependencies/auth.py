import sys
from uuid import UUID
from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def _ensure_shared_package_available() -> None:
    current = Path(__file__).resolve()
    candidates = [current.parents[2], current.parents[3]]
    for candidate in candidates:
        if candidate.exists() and str(candidate) not in sys.path and (candidate / "shared").exists():
            sys.path.append(str(candidate))


_ensure_shared_package_available()

from shared.jwt_utils import verify_token  # noqa: E402


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется токен доступа")

    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="В токене нет идентификатора пользователя")

    user = db.get(User, UUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь недоступен")

    return user
