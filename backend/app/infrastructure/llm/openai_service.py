import os
from typing import Iterable
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

class OpenAILLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def stream_answer(self, *, question: str, context_chunks: Iterable[str]) -> Iterable[str]:
        context = "\n\n".join([f"- {c}" for c in context_chunks])
        system = (
            "Eres un asistente que SOLO responde usando el contexto proporcionado.\n"
            "Si la respuesta no está en el contexto, responde exactamente:\n"
            "\"No poseo información sobre ese tema en el documento cargado.\""
        )
        user = f"Pregunta: {question}\n\nContexto:\n{context}"
        stream = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            stream=True,
            temperature=0.1
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and getattr(delta, "content", None):
                yield delta.content
