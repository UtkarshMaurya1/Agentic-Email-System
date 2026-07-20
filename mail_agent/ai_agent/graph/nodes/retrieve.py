from datetime import datetime, timezone

from knowledge_base.ingestion.embedder import embed_text
from knowledge_base.models import KBChunk
from pgvector.django import CosineDistance

TOP_K = 3


def _log(node_name: str, note: str = "") -> dict:
    return {"node": node_name, "timestamp": datetime.now(timezone.utc).isoformat(), "summary": note}


def retrieve_kb(state):
    query = state["raw_email"].get("body", "")
    query_vec = embed_text(query)

    chunks = (
        KBChunk.objects
        .select_related("document")
        .annotate(distance=CosineDistance("embedding",  query_vec))
        .order_by("distance")[:TOP_K]
    )

    for chunk in chunks:
        print(f"Chunk Distance := {chunk.distance}")

    retrieved_context = [
        {"text": c.text, "source_doc": c.document.title, "section": c.section_label}
        for c in chunks
    ]

    return {
        "retrieved_context": retrieved_context,
        "audit_trail": [_log("retrieve_kb", f"retrieved {len(retrieved_context)} chunks")],
    }