import os
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

class OpenAIEmbeddingsService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(model=EMBED_MODEL, input=texts)
        return [d.embedding for d in resp.data]

    def embed_query(self, text: str) -> List[float]:
        return self.embed([text])[0]
