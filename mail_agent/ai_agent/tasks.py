from celery import shared_task

from ai_agent.graph.runner import run_email_agent
from ai_agent.models import AgentRun


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_email_task(self, thread_id: str, message_id: str, raw_email: dict):
    """
    Entry point from Celery. One task per inbound email.
    thread_id should be stable per conversation (e.g. email thread/subject
    normalized, or provider's thread id) so the checkpointer + AgentRun
    correctly track ongoing conversations.
    """
    # Dedup guard: don't reprocess an email we've already run to completion.
    existing = AgentRun.objects.filter(message_id=message_id, status="completed").first()
    if existing:
        return {"skipped": True, "reason": "already processed", "message_id": message_id}

    try:
        result = run_email_agent(thread_id, message_id, raw_email)
    except Exception as exc:
        # Transient errors (LLM timeout, DB hiccup) -> retry with backoff.
        raise self.retry(exc=exc)

    return {
        "thread_id": thread_id,
        "action": result.get("action"),
        "approval_status": result.get("approval_status"),
        "interrupted": "__interrupt__" in result,
    }