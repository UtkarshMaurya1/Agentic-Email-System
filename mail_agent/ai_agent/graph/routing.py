def route_after_classification(state) -> str:
    if state['category'] in ("spam", "auto_reply"):
        return "discard"
    
    if state['needs_knowledge']:
        return "retrieve_kb"
    
    return "generate_reply"

def route_after_decision(state) -> str:
    return {
        "discard": "log_and_audit",
        "auto_send": "send_email",
        "needs_approval": "await_approval",
        "notify_only": "notify_human",
    }[state["action"]]