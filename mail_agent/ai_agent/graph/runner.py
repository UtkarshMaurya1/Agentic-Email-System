from django.conf import settings

from ai_agent.graph.graph_builder import get_compiled_graph

_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = get_compiled_graph(settings.LANGGRAPH_DB_URI)
    return _compiled_graph


def run_email_agent(thread_id: str, message_id: str, raw_email: dict):
    """Entry point called from a Celery task."""
    graph = _get_graph()
    initial_state = {
        "thread_id": thread_id,
        "message_id": message_id,
        "raw_email": raw_email,
        "retrieved_context": [],
        "risk_flags": [],
        "audit_trail": [],
        "errors": [],
    }
    config = {"configurable": {"thread_id": thread_id}}
    return graph.invoke(initial_state, config=config)