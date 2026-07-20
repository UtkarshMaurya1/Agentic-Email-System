from datetime import datetime, timezone


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def _actually_notify(message: str) -> None:
    """
    TODO: wire to a real channel (Slack webhook, email) once notifications
    app exists. For now, a clear seam + console output.
    """
    print(f"[STUB NOTIFY] {message}")


def notify_human(state):
    message = (
        f"Urgent email needs attention — category={state.get('category')}, "
        f"urgency={state.get('urgency')}, thread={state['thread_id']}"
    )
    _actually_notify(message)
    return {"audit_trail": [_log("notify_human", "notification dispatched")]}