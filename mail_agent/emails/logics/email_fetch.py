"""
Fetches unread emails from Gmail via IMAP using an app password.
"""
import email
import imaplib
import os
from email.header import decode_header

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

    Does NOT mark emails as read here — dedup is handled downstream via
    AgentRun.message_id, so re-fetching an already-processed email is safe
    (the Celery task skips it). Marking read/unread is left as a later
    decision (see note at bottom).
    """
    address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    conn = imaplib.IMAP4_SSL(IMAP_HOST)
    conn.login(address, app_password)
    conn.select("INBOX")

    status, data = conn.search(None, "UNSEEN")
    results = []

    if status == "OK":
        for num in data[0].split():
            status, msg_data = conn.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            raw_msg = msg_data[0][1]
            msg = email.message_from_bytes(raw_msg)

            message_id = msg.get("Message-ID", "").strip()
            # Gmail threads: References/In-Reply-To chain back to the first
            # Message-ID in a thread. Use References' first entry as thread_id,
            # falling back to this message's own id for a new thread.
            references = msg.get("References", "")
            thread_id = references.split()[0].strip() if references else message_id

            results.append({
                "message_id": message_id,
                "thread_id": thread_id,
                "subject": _decode(msg.get("Subject", "")),
                "body": _extract_body(msg),
                "from": _decode(msg.get("From", "")),
            })

    conn.close()
    conn.logout()
    return results

# NOTE on marking emails read: intentionally not doing so here. If the
# Celery task fails after fetch but before processing, you want the email
# fetchable again next poll. Dedup via AgentRun.message_id (see ai_agent/tasks.py)
# is the safer guard than relying on IMAP's \Seen flag for idempotency.