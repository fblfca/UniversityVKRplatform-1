import bcrypt
import random
import string
from datetime import datetime, timedelta, timezone


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def generate_login_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def get_code_expiration(ttl_minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
