from datetime import datetime, timezone

from emails.logics.email_send import send_notification


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def notify_human(state):
    subject = f"[URGENT] {state.get('category', 'email')} needs attention"
    body = (
        f"Category: {state.get('category')}\n"
        f"Urgency: {state.get('urgency')}\n"
        f"Sentiment: {state.get('sentiment')}\n"
        f"Thread: {state['thread_id']}\n\n"
        f"Original message:\n{state['raw_email'].get('body', '')}\n\n"
        f"Draft response (if generated):\n{state.get('draft_response', '(none)')}"
    )

    try:
        send_notification(subject, body)
        note = "notification email sent"
    except Exception as e:
        note = f"notification send failed: {e}"

    return {"audit_trail": [_log("notify_human", note)]}