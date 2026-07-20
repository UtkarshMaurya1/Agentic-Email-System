import json
from datetime import datetime, timezone

from ai_agent.graph.llm_provider import call_llm

ANALYZE_PROMPT_TEMPLATE = """You are analyzing a customer support email for a travel booking service.

Email subject: {subject}
Email body:
{body}

Respond with ONLY a JSON object, no other text, in this exact shape:
{{
  "issue_type": "<short label, e.g. itinerary_question, booking_change, cancellation_refund, complaint, general_inquiry, spam>",
  "category": "<same value as issue_type>",
  "urgency": "<low|medium|high|critical>",
  "sentiment": "<positive|neutral|negative|angry>"
}}
"""


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def analyze_email(state):
    email = state["raw_email"]
    prompt = ANALYZE_PROMPT_TEMPLATE.format(
        subject=email.get("subject", ""), body=email.get("body", "")
    )

    try:
        raw_output = call_llm(
            prompt,
            system_prompt="You output ONLY valid JSON, with no markdown code fences and no extra text.",
        )
        raw_output = raw_output.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw_output)
    except (json.JSONDecodeError, Exception) as e:
        # Fail safe: unknown category forces human review downstream
        return {
            "issue_type": "unknown",
            "category": "unknown",
            "urgency": "medium",
            "sentiment": "neutral",
            "errors": [{"node": "analyze_email", "error": str(e)}],
            "audit_trail": [_log("analyze_email", "LLM parse failed, defaulted to unknown/medium")],
        }

    return {
        "issue_type": parsed.get("issue_type", "unknown"),
        "category": parsed.get("category", parsed.get("issue_type", "unknown")),
        "urgency": parsed.get("urgency", "medium"),
        "sentiment": parsed.get("sentiment", "neutral"),
        "audit_trail": [_log("analyze_email", f"category={parsed.get('category')}, urgency={parsed.get('urgency')}")],
    }