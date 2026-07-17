"""
Thin wrapper around the embedding model so it's a config change, not a
refactor, if you swap models later. Using a local sentence-transformers
model keeps this free/offline for a learning project.
"""
from functools import lru_cache
from sentence_transformers import SentenceTransformer
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim, matches KBChunk.embedding dimensions


@lru_cache(maxsize=1)
def _get_model():    
    print("Loading embedding model...")
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    model = _get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts, normalize_embeddings=True).tolist()
