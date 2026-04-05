import random
import string
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_login_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def get_code_expiration(ttl_minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
