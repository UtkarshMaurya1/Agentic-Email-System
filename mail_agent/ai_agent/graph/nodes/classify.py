from datetime import datetime, timezone

KNOWLEDGE_CATEGORIES = {"itinerary_question", "destination_info"}


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def classify_and_route(state):
    needs_knowledge = state["category"] in KNOWLEDGE_CATEGORIES
    return {
        "needs_knowledge": needs_knowledge,
        "audit_trail": [_log("classify_and_route", f"needs_knowledge={needs_knowledge}")],
    }