from django.core.management.base import BaseCommand, CommandError

from knowledge_base.ingestion.chunker import chunk_pdf
from knowledge_base.ingestion.embedder import embed_batch
from knowledge_base.models import KBDocument, KBChunk


class Command(BaseCommand):
    help = "Ingest a PDF (e.g. travel itinerary) into the knowledge base."

    def add_arguments(self, parser):
        parser.add_argument("pdf_path", type=str)
        parser.add_argument(
            "--title", type=str, default=None,
            help="Display title; defaults to filename",
        )
        parser.add_argument(
            "--doc-type", type=str, default="itinerary",
        )

    def handle(self, *args, **options):
        pdf_path = options["pdf_path"]
        title = options["title"] or pdf_path.split("/")[-1]

        try:
            chunks = chunk_pdf(pdf_path)
        except FileNotFoundError:
            raise CommandError(f"File not found: {pdf_path}")

        if not chunks:
            raise CommandError("No text extracted — is this a scanned/image PDF?")

        self.stdout.write(f"Extracted {len(chunks)} chunks. Embedding...")
        embeddings = embed_batch([c.text for c in chunks])

        document = KBDocument.objects.create(
            title=title, source_path=pdf_path, doc_type=options["doc_type"]
        )
        KBChunk.objects.bulk_create([
            KBChunk(
                document=document,
                chunk_index=c.chunk_index,
                section_label=c.section_label,
                text=c.text,
                embedding=emb,
            )
            for c, emb in zip(chunks, embeddings)
        ])

        self.stdout.write(self.style.SUCCESS(
            f"Ingested '{title}' as {len(chunks)} chunks (doc id={document.id})."
        ))