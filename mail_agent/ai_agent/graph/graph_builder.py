from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from ai_agent.graph.state import EmailAgentState
from ai_agent.graph.routing import route_after_classification, route_after_decision
from ai_agent.graph.nodes import stubs


def build_graph(checkpointer):
    graph = StateGraph(EmailAgentState)

    graph.add_node("ingest_email", stubs.ingest_email)
    graph.add_node("analyze_email", stubs.analyze_email)
    graph.add_node("classify_and_route", stubs.classify_and_route)
    graph.add_node("retrieve_kb", stubs.retrieve_kb)
    graph.add_node("generate_reply", stubs.generate_reply)
    graph.add_node("decide_action", stubs.decide_action)
    graph.add_node("send_email", stubs.send_email)
    graph.add_node("await_approval", stubs.await_approval)
    graph.add_node("notify_human", stubs.notify_human)
    graph.add_node("log_and_audit", stubs.log_and_audit)

    graph.add_edge(START, "ingest_email")
    graph.add_edge("ingest_email", "analyze_email")
    graph.add_edge("analyze_email", "classify_and_route")

    graph.add_conditional_edges(
        "classify_and_route",
        route_after_classification,
        {"retrieve_kb": "retrieve_kb", "generate_reply": "generate_reply", "discard": "log_and_audit"},
    )
    graph.add_edge("retrieve_kb", "generate_reply")
    graph.add_edge("generate_reply", "decide_action")

    graph.add_conditional_edges(
        "decide_action",
        route_after_decision,
        {
            "send_email": "send_email",
            "await_approval": "await_approval",
            "notify_human": "notify_human",
            "log_and_audit": "log_and_audit",
        },
    )

    graph.add_edge("send_email", "log_and_audit")
    graph.add_edge("await_approval", "log_and_audit")  # Phase D: interrupt lives here
    graph.add_edge("notify_human", "log_and_audit")
    graph.add_edge("log_and_audit", END)

    return graph.compile(checkpointer=checkpointer)


def get_compiled_graph(db_uri: str):
    """Call once (e.g. at Celery worker startup) and reuse the compiled graph."""
    checkpointer_cm = PostgresSaver.from_conn_string(db_uri)
    checkpointer = checkpointer_cm.__enter__()  # kept open for app lifetime
    checkpointer.setup()  # creates checkpoint tables if not present
    return build_graph(checkpointer)