"""
Fetches unread emails from Gmail via IMAP using an app password.
"""
import email
import imaplib
import os
from email.header import decode_header
from email.utils import parseaddr

from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = "imap.gmail.com"


def _decode(value: str) -> str:
    if not value:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def _extract_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in disposition:
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="ignore")
        return ""
    else:
        charset = msg.get_content_charset() or "utf-8"
        return msg.get_payload(decode=True).decode(charset, errors="ignore")


def fetch_unread_emails() -> list[dict]:
    """
    Returns a list of dicts:
    {"message_id": str, "thread_id": str, "subject": str, "body": str, "from": str}

    Only fetches unread mail from Gmail's "Primary" category (excludes
    Promotions/Social/Updates), using Gmail's IMAP search extension.
    Also skips any email sent from our own address, to avoid re-ingesting
    our own notification/alert emails as if they were customer messages.

    Does NOT mark emails as read here — dedup is handled downstream via
    AgentRun.message_id, so re-fetching an already-processed email is safe
    (the Celery task skips it).
    """
    address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    conn = imaplib.IMAP4_SSL(IMAP_HOST)
    conn.login(address, app_password)
    conn.select("INBOX")

    # Gmail-specific search extension: restrict to Primary tab + unread.
    status, data = conn.uid("search", None, "X-GM-RAW", '"category:primary is:unread"')
    results = []

    if status == "OK":
        uids = data[0].split()
        for uid in uids:
            status, msg_data = conn.uid("fetch", uid, "(RFC822)")
            if status != "OK" or not msg_data or msg_data[0] is None:
                continue

            raw_msg = msg_data[0][1]
            msg = email.message_from_bytes(raw_msg)

            sender_raw = _decode(msg.get("From", ""))
            _, sender_address = parseaddr(sender_raw)
            if sender_address.lower() == address.lower():
                continue  # skip our own self-sent notification/alert emails

            message_id = msg.get("Message-ID", "").strip()
            references = msg.get("References", "")
            thread_id = references.split()[0].strip() if references else message_id

            results.append({
                "message_id": message_id,
                "thread_id": thread_id,
                "subject": _decode(msg.get("Subject", "")),
                "body": _extract_body(msg),
                "from": sender_raw,
            })

    conn.close()
    conn.logout()
    return results

# NOTE on marking emails read: intentionally not doing so here. If the
# Celery task fails after fetch but before processing, you want the email
# fetchable again next poll. Dedup via AgentRun.message_id (see ai_agent/tasks.py)
# is the safer guard than relying on IMAP's \Seen flag for idempotency.