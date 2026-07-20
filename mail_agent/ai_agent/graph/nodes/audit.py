from datetime import datetime, timezone

from django.utils import timezone as dj_timezone

from ai_agent.models import AgentRun, AgentAuditLog


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def log_and_audit(state):
    final_text = state.get("human_edited_response") or state.get("draft_response")

    run, _ = AgentRun.objects.update_or_create(
        langgraph_thread_id=state["thread_id"],
        defaults={
            "message_id": state["message_id"],
            "issue_type": state.get("issue_type"),
            "urgency": state.get("urgency"),
            "sentiment": state.get("sentiment"),
            "category": state.get("category"),
            "action_taken": state.get("action"),
            "draft_response": state.get("draft_response"),
            "final_response": final_text,
            "status": "completed",
            "completed_at": dj_timezone.now(),
        },
    )

    AgentAuditLog.objects.bulk_create([
        AgentAuditLog(run=run, node_name=entry["node"], summary=entry.get("summary", ""))
        for entry in state.get("audit_trail", [])
    ])

    return {"audit_trail": [_log("log_and_audit", "run persisted")]}