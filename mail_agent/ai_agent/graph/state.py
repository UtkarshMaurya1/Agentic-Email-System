import operator
from typing import TypedDict, Annotated, Literal

class EmailAgentState(TypedDict):
    thread_id: str
    message_id: str
    raw_email: dict

    issue_type: str | None
    urgency: Literal['low', 'medium', 'high', 'critical'] | None
    sentiment: Literal["positive", "neutral", "negative", "angry"] | None
    category : str | None

    needs_knowledge: bool
    retrieved_context: list[dict]
 
    draft_response: str | None
    risk_flags: list[str]
    action: Literal["auto_send", "needs_approval", "notify_only", "discard"] | None
 
    approval_status: Literal["pending", "approved", "edited", "rejected"] | None
    human_edited_response: str | None
 
    audit_trail: Annotated[list[dict], operator.add]
    errors: Annotated[list[dict], operator.add]




