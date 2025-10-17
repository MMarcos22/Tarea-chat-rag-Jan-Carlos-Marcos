from typing import Protocol, Iterable

class LLMService(Protocol):
    def stream_answer(self, *, question: str, context_chunks: Iterable[str]) -> Iterable[str]: ...
