"""
Standalone sanity check for retrieval quality — run this BEFORE wiring
RAG into the LangGraph node. Usage (from Django shell or a script
run via `manage.py shell < test_retrieval.py`, adjusted to your setup):

    from knowledge_base.ingestion.test_retrieval import search
    search("What are we doing on day 3 in Kyoto?")
"""
from knowledge_base.ingestion.embedder import embed_text
from knowledge_base.models import KBChunk

from pgvector.django import CosineDistance

def search(query: str, top_k: int = 3):
    query_vec = embed_text(query)

    results = (
        KBChunk.objects
        .order_by(CosineDistance("embedding", query_vec))
        [:top_k]
    )

    for i, chunk in enumerate(results, start=1):
        print(f"\n--- Result {i} (doc: {chunk.document.title}, section: {chunk.section_label}) ---")
        print(chunk.text[:400])

    return results