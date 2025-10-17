from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 IMPORTANTE

from app.interfaces.http.routes_documents import build_routes
from app.interfaces.ws.socket_server import build_socket
from app.infrastructure.db.repositories_pg import PgDocumentRepository, JsonVectorRepository
from app.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddingsService
from app.infrastructure.llm.openai_service import OpenAILLMService
from app.application.use_cases.UploadDocumentUseCase import UploadDocumentUseCase
from app.application.use_cases.AskQuestionUseCase import AskQuestionUseCase


def create_app():
    docs_repo = PgDocumentRepository()
    vec_repo  = JsonVectorRepository()
    emb       = OpenAIEmbeddingsService()
    llm       = OpenAILLMService()

    upload_uc = UploadDocumentUseCase(docs_repo, vec_repo, emb)
    ask_uc    = AskQuestionUseCase(vec_repo, emb, llm)

    app = FastAPI(title="RAG + Sockets API")

    # 👇 Habilita CORS para que el preflight OPTIONS funcione
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],   # incluye OPTIONS
        allow_headers=["*"],
    )

    app.include_router(build_routes(upload_uc))
    asgi_app = build_socket(app, ask_uc)
    return asgi_app


app = create_app()

if __name__ == "__main__":
    import socket
    host = socket.gethostbyname(socket.gethostname())
    print(f"\nServidor corriendo en:")
    print(f"Localhost: http://127.0.0.1:8000")
    print(f"Red local: http://{host}:8000\n")

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
