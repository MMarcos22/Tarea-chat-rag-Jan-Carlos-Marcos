
from uuid import UUID
from typing import Optional
from app.domain.repositories.DocumentRepository import DocumentRepository
from app.domain.repositories.VectorRepository import VectorRepository
from app.domain.services.EmbeddingsService import EmbeddingsService
from io import BytesIO
from pdfminer.high_level import extract_text


class UploadDocumentUseCase:
    def __init__(self, docs_repo: DocumentRepository, vec_repo: VectorRepository, emb: EmbeddingsService):
        self.docs_repo = docs_repo
        self.vec_repo = vec_repo
        self.emb = emb

    def _chunk_text(self, text: str, max_chars: int = 1200):
        chunks = []
        for i in range(0, len(text), max_chars):
            chunk_text = text[i:i+max_chars]
            if chunk_text.strip():
                chunks.append({ "chunk_index": len(chunks), "content": chunk_text })
        return chunks

    def execute(self, *, title: str, filename: str, mime_type: str, file_bytes: bytes, owner_id: Optional[UUID]) -> UUID:
        # 1) Guardar PDF
        doc_id = self.docs_repo.save_pdf(
            title=title, filename=filename, mime_type=mime_type,
            file_bytes=file_bytes, owner_id=owner_id
        )
        # 2) Extraer texto y chunkear
        text = extract_text(BytesIO(file_bytes))
        chunks = self._chunk_text(text)
        chunk_ids = self.docs_repo.add_chunks(doc_id, chunks)

        # 3) Embeddings
        texts = [c["content"] for c in chunks]
        vectors = self.emb.embed(texts)
        pairs = list(zip(chunk_ids, vectors))
        self.vec_repo.upsert_embeddings(pairs)

        return doc_id
