import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import LOGIN_CODE_TTL_MINUTES, SHOW_LOGIN_CODE, access_token_ttl
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import LoginCode, User
from app.schemas.auth import (
    BatchUsersRequest,
    BatchUsersResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
    VerifyRequest,
    VerifyResponse,
)
from app.utils.security import generate_login_code, get_code_expiration, hash_password, verify_password


def _ensure_shared_package_available() -> None:
    current = Path(__file__).resolve()
    candidates = [current.parents[2], current.parents[3]]
    for candidate in candidates:
        if candidate.exists() and str(candidate) not in sys.path and (candidate / "shared").exists():
            sys.path.append(str(candidate))


_ensure_shared_package_available()

from shared.jwt_utils import create_access_token  # noqa: E402


router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким email уже существует")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    now = get_code_expiration(0)
    db.execute(
        update(LoginCode)
        .where(LoginCode.user_id == user.id, LoginCode.consumed_at.is_(None))
        .values(consumed_at=now)
    )

    code = generate_login_code()
    login_code = LoginCode(
        user_id=user.id,
        code=code,
        expires_at=get_code_expiration(LOGIN_CODE_TTL_MINUTES),
    )
    db.add(login_code)
    db.commit()
    db.refresh(login_code)

    return LoginResponse(
        message="Код входа создан. Пока email-service не подключен, код возвращается в ответе для тестирования.",
        code_expires_at=login_code.expires_at,
        debug_code=code if SHOW_LOGIN_CODE else None,
    )


@router.post("/verify", response_model=VerifyResponse)
def verify_login_code(payload: VerifyRequest, db: Session = Depends(get_db)) -> VerifyResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    login_code = db.scalar(
        select(LoginCode)
        .where(
            LoginCode.user_id == user.id,
            LoginCode.code == payload.code,
            LoginCode.consumed_at.is_(None),
        )
        .order_by(LoginCode.created_at.desc())
    )
    if login_code is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Код не найден или уже использован")

    now = get_code_expiration(0)
    if login_code.expires_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Срок действия кода истек")

    login_code.consumed_at = now
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        },
        expires_delta=access_token_ttl(),
    )

    return VerifyResponse(access_token=access_token, user=user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/batch/users", response_model=BatchUsersResponse)
def batch_users(payload: BatchUsersRequest, db: Session = Depends(get_db)) -> BatchUsersResponse:
    if not payload.user_ids:
        return BatchUsersResponse(users=[])

    users = db.scalars(select(User).where(User.id.in_(payload.user_ids))).all()
    return BatchUsersResponse(users=list(users))


@router.post("/internal/users/batch", response_model=BatchUsersResponse)
def internal_batch_users(payload: BatchUsersRequest, db: Session = Depends(get_db)) -> BatchUsersResponse:
    return batch_users(payload, db)
