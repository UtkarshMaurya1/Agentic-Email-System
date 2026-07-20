"""
Sends email replies via Gmail SMTP using an app password
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
    to_address: raw "From" header value from the original email - parsed automatically.
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