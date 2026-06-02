from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from hashlib import sha256
import logging
import secrets
import smtplib

from app.config import Settings


logger = logging.getLogger(__name__)


def create_verification_token() -> str:
    return secrets.token_urlsafe(32)


def hash_verification_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def verification_expiration(settings: Settings) -> datetime:
    return datetime.now(UTC) + timedelta(minutes=settings.email_verification_expires_minutes)


def build_verification_link(settings: Settings, token: str) -> str:
    return f"{settings.public_ui_url}/?verify_email_token={token}"


def send_verification_email(settings: Settings, recipient: str, token: str) -> None:
    verification_link = build_verification_link(settings, token)

    if not settings.smtp_host:
        logger.info("Email verification link for %s: %s", recipient, verification_link)
        return

    message = EmailMessage()
    message["Subject"] = "Verify your Automotive Control account"
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message.set_content(
        "Confirm your account for the autonomous vehicle control platform:\n\n"
        f"{verification_link}\n\n"
        "If you did not create this account, ignore this email."
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)

