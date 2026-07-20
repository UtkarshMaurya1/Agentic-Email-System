import re
from datetime import datetime, timezone

from ai_agent.graph.llm_provider import call_llm

GENERATE_PROMPT_TEMPLATE = """You are a helpful travel support assistant. Write a reply to this customer email.

Category: {category}
Sentiment: {sentiment}

Customer email:
{body}

Relevant knowledge base context (use only if relevant, do not invent facts beyond this):
{context}

Write a clear, friendly, concise reply. Do not promise refunds, discounts, or make
legal/policy commitments beyond what's in the context.
"""

RISK_PATTERNS = {
    "refund_mentioned": re.compile(r"\brefund(ed|ing)?\b", re.IGNORECASE),
    "price_commitment": re.compile(r"\b(discount|free upgrade|price match|waive)\b", re.IGNORECASE),
    "legal_language": re.compile(r"\b(guarantee|promise|liable|legal)\b", re.IGNORECASE),
}


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def _scan_risk_flags(text: str) -> list[str]:
    return [flag for flag, pattern in RISK_PATTERNS.items() if pattern.search(text)]


def generate_reply(state):
    context_text = "\n\n".join(
        f"[{c['source_doc']} - {c.get('section', '')}]\n{c['text']}"
        for c in state.get("retrieved_context", [])
    ) or "(no relevant context found)"

    prompt = GENERATE_PROMPT_TEMPLATE.format(
        category=state.get("category"),
        sentiment=state.get("sentiment"),
        body=state["raw_email"].get("body", ""),
        context=context_text,
    )

    try:
        draft = call_llm(prompt)
    except Exception as e:
        return {
            "draft_response": None,
            "risk_flags": ["generation_failed"],
            "errors": [{"node": "generate_reply", "error": str(e)}],
            "audit_trail": [_log("generate_reply", "LLM call failed")],
        }

    risk_flags = _scan_risk_flags(draft)

    # No grounded context but the category needed knowledge -> force review
    if state.get("needs_knowledge") and not state.get("retrieved_context"):
        risk_flags.append("ungrounded_response")

    return {
        "draft_response": draft,
        "risk_flags": risk_flags,
        "audit_trail": [_log("generate_reply", f"risk_flags={risk_flags}")],
    }