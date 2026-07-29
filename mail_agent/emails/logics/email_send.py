"""
Sends emails via Gmail SMTP using an app password (same credentials
as email_fetch.py — GMAIL_ADDRESS / GMAIL_APP_PASSWORD in .env).
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import parseaddr

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def send_reply(to_address: str, subject: str, body: str, in_reply_to: str | None = None) -> None:
    """
    to_address: raw "From" header value from the original email 
    in_reply_to: original Message-ID, sets proper threading headers so the
                 reply lands in the same Gmail conversation.
    """
    address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    _, clean_to_address = parseaddr(to_address)
    if not clean_to_address:
        raise ValueError(f"Could not parse a valid email address from: {to_address!r}")

    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"

    msg = MIMEText(body)
    msg["Subject"] = reply_subject
    msg["From"] = address
    msg["To"] = clean_to_address
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(address, app_password)
        server.sendmail(address, [clean_to_address], msg.as_string())


def send_notification(subject: str, body: str) -> None:
    """
    Sends a plain (non-threaded) alert email to yourself — used for
    critical-urgency notifications, not customer replies.
    Recipient is your own GMAIL_ADDRESS unless NOTIFY_TO_ADDRESS is set.
    """
    address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    notify_to = os.environ.get("NOTIFY_TO_ADDRESS", address)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = address
    msg["To"] = notify_to

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(address, app_password)
        server.sendmail(address, [notify_to], msg.as_string())