from datetime import datetime, timezone

KNOWLEDGE_CATEGORIES = {"itinerary_question", "destination_info"}
LOW_MEDIUM_URGENCY = {"low", "medium"}
SAFE_SENTIMENT = {"neutral", "positive"}


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def decide_action(state):
    category = state.get("category")
    urgency = state.get("urgency")
    sentiment = state.get("sentiment")
    risk_flags = state.get("risk_flags") or []
    retrieved_context = state.get("retrieved_context") or []

    if category in ("spam", "auto_reply"):
        action = "discard"
    elif urgency == "critical":
        action = "notify_only"
    elif risk_flags:
        action = "needs_approval"
    elif sentiment == "angry" and category == "complaint":
        action = "needs_approval"
    elif (
        category in KNOWLEDGE_CATEGORIES
        and urgency in LOW_MEDIUM_URGENCY
        and sentiment in SAFE_SENTIMENT
        and retrieved_context
        and not risk_flags
    ):
        action = "auto_send"
    else:
        action = "needs_approval"

    return {"action": action, "audit_trail": [_log("decide_action", f"action={action}")]}