"""
ADJUST: replace `fetch_unread_emails` import/call below to match your
actual emails/logics/email_fetch.py function name and return shape.
Assumed here: it returns a list of dicts like
    {"message_id": str, "thread_id": str, "subject": str, "body": str, "from": str}
"""
from celery import shared_task

from ai_agent.tasks import process_email_task
from emails.logics.email_fetch import fetch_unread_emails 


@shared_task
def poll_unread_emails_task():
    """
    Run on a schedule (see CELERY_BEAT_SCHEDULE in settings).
    Fetches unread emails and fans out one process_email_task per email.
    """
    emails = fetch_unread_emails()
    dispatched = 0

    for email in emails:
        message_id = email.get("message_id")
        thread_id = email.get("thread_id") or message_id  # fallback if no thread grouping
        if not message_id:
            continue  # can't dedup/checkpoint without a stable id — skip and log elsewhere

        process_email_task.delay(
            thread_id=thread_id,
            message_id=message_id,
            raw_email={
                "subject": email.get("subject", ""),
                "body": email.get("body", ""),
                "from": email.get("from", "unknown"),
            },
        )
        dispatched += 1

    return {"dispatched": dispatched}