from datetime import datetime, timezone

from ai_agent.models import AgentRun
from emails.logics.email_send import send_reply


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def send_email(state):
    final_text = state.get("human_edited_response") or state.get("draft_response")

    # Idempotency guard: don't send twice for the same message_id.
    run = AgentRun.objects.filter(langgraph_thread_id=state["thread_id"]).first()
    if run and run.status == "completed":
        return {"audit_trail": [_log("send_email", "skipped — already completed for this thread")]}

    to_address = state["raw_email"].get("from") or state["raw_email"].get("sender", "unknown")
    subject = state["raw_email"].get("subject", "your inquiry")
    original_message_id = state.get("message_id")

    try:
        send_reply(to_address, subject, final_text or "", in_reply_to=original_message_id)
    except Exception as e:
        return {
            "errors": [{"node": "send_email", "error": str(e)}],
            "audit_trail": [_log("send_email", f"send failed: {e}")],
        }

    return {"audit_trail": [_log("send_email", f"sent to {to_address}")]}