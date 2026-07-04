"""
auth_service.py
-----------------
All password-hashing, OTP, and email-sending helper functions live
here so that routes/auth.py stays clean and focused on request
handling.
"""

import bcrypt
import random
import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import Config


def hash_password(plain_password: str) -> str:
    """Turn a plain text password into a secure bcrypt hash (string)."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain text password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def generate_otp() -> str:
    """Generate a random 6 digit OTP as a string, e.g. '482913'."""
    return str(random.randint(100000, 999999))


def get_otp_expiry(minutes: int = 5) -> datetime.datetime:
    """Return the datetime at which a freshly generated OTP should expire."""
    return datetime.datetime.now() + datetime.timedelta(minutes=minutes)


def is_otp_valid(stored_otp: str, entered_otp: str, expiry: datetime.datetime) -> bool:
    """Check the OTP matches and that it has not expired yet."""
    if stored_otp is None or expiry is None:
        return False
    if stored_otp != entered_otp:
        return False
    if datetime.datetime.now() > expiry:
        return False
    return True


def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Sends the OTP to the user's real email address using SMTP
    (configured for Gmail by default in config.py).

    Returns True if the email was sent successfully, False otherwise.
    If MAIL_DEBUG_PRINT_OTP is True in config.py, the OTP is also
    printed to the console as a fallback so you're never locked out
    during development.
    """
    if Config.MAIL_DEBUG_PRINT_OTP:
        print(f"[DEV] OTP for {to_email} is: {otp}")

    # Build the email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your AI Portfolio Builder OTP Code"
    message["From"] = f"{Config.MAIL_FROM_NAME} <{Config.MAIL_USERNAME}>"
    message["To"] = to_email

    plain_text = (
        f"Your OTP code is: {otp}\n\n"
        f"This code will expire in {Config.OTP_EXPIRY_MINUTES} minutes.\n"
        f"If you did not request this, you can safely ignore this email."
    )

    html_text = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color: #4f46e5;">AI Portfolio Builder</h2>
        <p>Your OTP code is:</p>
        <p style="font-size: 32px; font-weight: bold; letter-spacing: 6px;
                   color: #3730a3;">{otp}</p>
        <p>This code will expire in {Config.OTP_EXPIRY_MINUTES} minutes.</p>
        <p style="color: #64748b; font-size: 13px;">
            If you did not request this, you can safely ignore this email.
        </p>
    </div>
    """

    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_text, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.ehlo()
            if Config.MAIL_USE_TLS:
                server.starttls(context=context)
                server.ehlo()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(Config.MAIL_USERNAME, to_email, message.as_string())
        return True
    except Exception as e:
        print(f"[Email Error] Could not send OTP email to {to_email}: {e}")
        return False