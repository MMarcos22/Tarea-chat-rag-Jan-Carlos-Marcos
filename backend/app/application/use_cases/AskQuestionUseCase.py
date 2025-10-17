from uuid import UUID
from app.domain.repositories.VectorRepository import VectorRepository
from app.domain.services.EmbeddingsService import EmbeddingsService
from app.domain.services.LLMService import LLMService


NO_INFO = "No poseo información sobre ese tema en el documento cargado."

class AskQuestionUseCase:
    def __init__(self, vec_repo: VectorRepository, emb: EmbeddingsService, llm: LLMService):
        self.vec_repo = vec_repo
        self.emb = emb
        self.llm = llm

    def stream(self, *, question: str, document_id: UUID | None = None):
        if not document_id:
            yield NO_INFO
            return
        q_emb = self.emb.embed_query(question)
        hits = self.vec_repo.search(q_emb, top_k=5, document_id=document_id)
        if not hits:
            yield NO_INFO
            return
        context_chunks = [h["content"] for h in hits]
        for token in self.llm.stream_answer(question=question, context_chunks=context_chunks):
            yield token
