import os
from datetime import timedelta


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
LOGIN_CODE_TTL_MINUTES = int(os.getenv("LOGIN_CODE_TTL_MINUTES", "10"))
SHOW_LOGIN_CODE = os.getenv("SHOW_LOGIN_CODE", "true").lower() == "true"
LOG_LOGIN_CODE = os.getenv("LOG_LOGIN_CODE", "true").lower() == "true"
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_AUTO_DETECT = os.getenv("EMAIL_AUTO_DETECT", "true").lower() == "true"
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"
EMAIL_USE_STARTTLS = os.getenv("EMAIL_USE_STARTTLS", "false").lower() == "true"
LOGIN_CODE_EMAIL_SUBJECT = os.getenv("LOGIN_CODE_EMAIL_SUBJECT", "Your VKR login code")


def access_token_ttl() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
