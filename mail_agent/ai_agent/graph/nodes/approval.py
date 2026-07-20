from datetime import datetime, timezone

from django.utils import timezone as dj_timezone
from langgraph.types import interrupt

from ai_agent.models import AgentRun, ApprovalRequest


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def await_approval(state):
    run, _ = AgentRun.objects.update_or_create(
        langgraph_thread_id=state["thread_id"],
        defaults={
            "message_id": state["message_id"],
            "original_subject": state["raw_email"].get("subject", ""),
            "original_sender": state["raw_email"].get("from", ""),
            "original_body": state["raw_email"].get("body", ""),
            "issue_type": state.get("issue_type"),
            "urgency": state.get("urgency"),
            "sentiment": state.get("sentiment"),
            "category": state.get("category"),
            "action_taken": state.get("action"),
            "draft_response": state.get("draft_response"),
            "status": "waiting_approval",
        },
    )
    approval_request, _ = ApprovalRequest.objects.get_or_create(run=run, decision=None)

    # This PAUSES graph execution here. State is checkpointed to Postgres.
    # Resuming happens via runner.resume_email_agent(thread_id, decision).
    decision = interrupt(
        {
            "reason": "human_approval_required",
            "draft_response": state.get("draft_response"),
            "category": state.get("category"),
            "risk_flags": state.get("risk_flags"),
        }
    )
    # `decision` is whatever value resume_email_agent() passes in via Command(resume=...)
    # Expected shape: {"decision": "approved"|"edited"|"rejected", "edited_text": str|None}

    approval_request.decision = decision.get("decision", "rejected")
    approval_request.edited_response = decision.get("edited_text")
    approval_request.decided_at = dj_timezone.now()
    approval_request.save()

    return {
        "approval_status": decision.get("decision", "rejected"),
        "human_edited_response": decision.get("edited_text"),
        "audit_trail": [_log("await_approval", f"resumed with decision={decision.get('decision')}")],
    }