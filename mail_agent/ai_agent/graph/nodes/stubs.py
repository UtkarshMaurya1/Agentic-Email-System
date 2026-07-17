"""
Stub nodes for Phase B — prove the graph shape works before adding real
logic (LLM calls, RAG, sending, approval) in Phase C/D.

Each stub just logs its name into audit_trail and returns minimal state
changes needed for routing to work.
"""
from datetime import datetime, timezone


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def ingest_email(state):
    return {"audit_trail": [_log("ingest_email", "email received")]}


def analyze_email(state):
    # Stub values — Phase C replaces this with a real LLM call
    return {
        "issue_type": "itinerary_question",
        "urgency": "low",
        "sentiment": "neutral",
        "category": "itinerary_question",
        "audit_trail": [_log("analyze_email", "stub analysis applied")],
    }


def classify_and_route(state):
    needs_knowledge = state["category"] in ("itinerary_question", "destination_info")
    return {
        "needs_knowledge": needs_knowledge,
        "audit_trail": [_log("classify_and_route", f"needs_knowledge={needs_knowledge}")],
    }


def retrieve_kb(state):
    # Stub — Phase C wires this to knowledge_base.ingestion.test_retrieval
    return {
        "retrieved_context": [{"text": "stub context", "source_doc": "stub.pdf", "score": 0.0}],
        "audit_trail": [_log("retrieve_kb", "stub retrieval")],
    }


def generate_reply(state):
    return {
        "draft_response": "This is a stub response.",
        "risk_flags": [],
        "audit_trail": [_log("generate_reply", "stub draft generated")],
    }


def decide_action(state):
    return {"action": "needs_approval", "audit_trail": [_log("decide_action", "stub -> needs_approval")]}


def send_email(state):
    return {"audit_trail": [_log("send_email", "stub send (no-op)")]}


def await_approval(state):
    return {
        "approval_status": "pending",
        "audit_trail": [_log("await_approval", "interrupt point reached")],
    }


def notify_human(state):
    return {"audit_trail": [_log("notify_human", "stub notification sent")]}


def log_and_audit(state):
    return {"audit_trail": [_log("log_and_audit", "run complete")]}