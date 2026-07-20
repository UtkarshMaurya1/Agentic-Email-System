from datetime import datetime, timezone

from ai_agent.models import AgentRun


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def _actually_send(to_address: str, subject: str, body: str) -> None:
    """
    TODO: wire this to your real emails app send logic
    (e.g. emails.logics.email_send.send_reply(...)) once it's built.
    Left as a clear seam so this node's structure doesn't change later.
    """
    print(f"[STUB SEND] to={to_address} subject={subject}\n{body}")


def send_email(state):
    final_text = state.get("human_edited_response") or state.get("draft_response")

    # Idempotency guard: don't send twice for the same message_id.
    run = AgentRun.objects.filter(langgraph_thread_id=state["thread_id"]).first()
    if run and run.status == "completed":
        return {"audit_trail": [_log("send_email", "skipped — already completed for this thread")]}

    to_address = state["raw_email"].get("from") or state["raw_email"].get("sender", "unknown")
    subject = state["raw_email"].get("subject", "Re: your inquiry")

    try:
        _actually_send(to_address, subject, final_text or "")
    except Exception as e:
        return {
            "errors": [{"node": "send_email", "error": str(e)}],
            "audit_trail": [_log("send_email", "send failed")],
        }

    return {"audit_trail": [_log("send_email", f"sent to {to_address}")]}