from django.db import models
from pgvector.django import HnswIndex, VectorField

class KBDocument(models.Model):
    title = models.CharField(max_length=255)
    source_path = models.CharField(max_length=500)  # original file path/name
    doc_type = models.CharField(
        max_length=50,
        default="itinerary",
        help_text="e.g. itinerary, policy, faq",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.title


class KBChunk(models.Model):
    document = models.ForeignKey(KBDocument, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.IntegerField()
    section_label = models.CharField(max_length=255, blank=True, help_text="e.g. 'Day 3 - Kyoto' — used for structured chunking")
    text = models.TextField()

    
    embedding = VectorField(dimensions=384)

    class Meta:
        indexes = [
            HnswIndex(
                name="kb_chunk_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]
 
    def __str__(self):
        return f"{self.document.title} [{self.section_label or self.chunk_index}]"
 