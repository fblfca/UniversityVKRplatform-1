from dataclasses import dataclass
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import (
    EMAIL_AUTO_DETECT,
    EMAIL_ENABLED,
    EMAIL_FROM,
    EMAIL_HOST,
    EMAIL_PASSWORD,
    EMAIL_PORT,
    EMAIL_USE_SSL,
    EMAIL_USE_STARTTLS,
    EMAIL_USER,
    LOGIN_CODE_EMAIL_SUBJECT,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SMTPSettings:
    host: str
    port: int
    use_ssl: bool
    use_starttls: bool


KNOWN_PROVIDERS: dict[str, list[SMTPSettings]] = {
    "gmail.com": [SMTPSettings(host="smtp.gmail.com", port=465, use_ssl=True, use_starttls=False)],
    "googlemail.com": [SMTPSettings(host="smtp.gmail.com", port=465, use_ssl=True, use_starttls=False)],
    "yandex.ru": [SMTPSettings(host="smtp.yandex.ru", port=465, use_ssl=True, use_starttls=False)],
    "ya.ru": [SMTPSettings(host="smtp.yandex.ru", port=465, use_ssl=True, use_starttls=False)],
    "yandex.com": [SMTPSettings(host="smtp.yandex.com", port=465, use_ssl=True, use_starttls=False)],
    "mail.com": [SMTPSettings(host="smtp.mail.com", port=465, use_ssl=True, use_starttls=False)],
    "gmx.com": [SMTPSettings(host="mail.gmx.com", port=465, use_ssl=True, use_starttls=False)],
    "outlook.com": [SMTPSettings(host="smtp-mail.outlook.com", port=587, use_ssl=False, use_starttls=True)],
    "hotmail.com": [SMTPSettings(host="smtp-mail.outlook.com", port=587, use_ssl=False, use_starttls=True)],
    "live.com": [SMTPSettings(host="smtp-mail.outlook.com", port=587, use_ssl=False, use_starttls=True)],
    "yahoo.com": [SMTPSettings(host="smtp.mail.yahoo.com", port=465, use_ssl=True, use_starttls=False)],
}


def _guess_smtp_settings(email_address: str) -> list[SMTPSettings]:
    domain = email_address.rsplit("@", 1)[-1].lower()
    if domain in KNOWN_PROVIDERS:
        return KNOWN_PROVIDERS[domain]

    return [
        SMTPSettings(host=f"smtp.{domain}", port=465, use_ssl=True, use_starttls=False),
        SMTPSettings(host=f"smtp.{domain}", port=587, use_ssl=False, use_starttls=True),
        SMTPSettings(host=f"mail.{domain}", port=465, use_ssl=True, use_starttls=False),
        SMTPSettings(host=f"mail.{domain}", port=587, use_ssl=False, use_starttls=True),
    ]


def _resolve_smtp_settings() -> list[SMTPSettings]:
    if EMAIL_HOST:
        return [
            SMTPSettings(
                host=EMAIL_HOST,
                port=EMAIL_PORT,
                use_ssl=EMAIL_USE_SSL,
                use_starttls=EMAIL_USE_STARTTLS,
            )
        ]

    if not EMAIL_AUTO_DETECT:
        return []

    candidate_email = EMAIL_USER or EMAIL_FROM
    if not candidate_email or "@" not in candidate_email:
        return []

    return _guess_smtp_settings(candidate_email)


def _open_smtp_client(settings: SMTPSettings) -> smtplib.SMTP | smtplib.SMTP_SSL:
    if settings.use_ssl:
        return smtplib.SMTP_SSL(settings.host, settings.port, timeout=30)
    return smtplib.SMTP(settings.host, settings.port, timeout=30)


def send_login_code_email(recipient: str, code: str) -> bool:
    if not EMAIL_ENABLED:
        logger.info("Email sending is disabled. Skip SMTP delivery for %s", recipient)
        return False

    if not EMAIL_FROM:
        logger.warning("Email sending is enabled, but sender address is not configured.")
        return False

    message = EmailMessage()
    message["Subject"] = LOGIN_CODE_EMAIL_SUBJECT
    message["From"] = EMAIL_FROM
    message["To"] = recipient
    message.set_content(
        "Your login code for VKR Platform: "
        f"{code}\n\n"
        "If you did not request this code, you can ignore this email."
    )

    smtp_settings_list = _resolve_smtp_settings()
    if not smtp_settings_list:
        logger.warning("Email sending is enabled, but SMTP settings could not be resolved.")
        return False

    for settings in smtp_settings_list:
        smtp_client: smtplib.SMTP | smtplib.SMTP_SSL | None = None
        try:
            smtp_client = _open_smtp_client(settings)
            if settings.use_starttls:
                smtp_client.starttls()
            if EMAIL_USER:
                smtp_client.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp_client.send_message(message)
            logger.info(
                "Login code email sent to %s via %s:%s",
                recipient,
                settings.host,
                settings.port,
            )
            return True
        except Exception:
            logger.exception(
                "Failed to send login code email to %s via %s:%s",
                recipient,
                settings.host,
                settings.port,
            )
        finally:
            if smtp_client is not None:
                try:
                    smtp_client.quit()
                except Exception:
                    logger.debug("SMTP connection cleanup failed", exc_info=True)

    return False
