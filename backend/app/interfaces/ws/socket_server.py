from fastapi import FastAPI
from socketio import AsyncServer
import socketio
from uuid import UUID
from app.application.use_cases.AskQuestionUseCase import AskQuestionUseCase, NO_INFO

def build_socket(app: FastAPI, ask_uc: AskQuestionUseCase):
    sio = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
    asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

    @sio.event
    async def connect(sid, environ):
        await sio.emit("server_ready", {"ok": True}, to=sid)

    @sio.event
    async def user_question(sid, data):
        question = (data or {}).get("question","").strip()
        document_id = (data or {}).get("document_id")
        doc_id = UUID(document_id) if document_id else None

        sent = False
        for piece in ask_uc.stream(question=question, document_id=doc_id):
            await sio.emit("bot_chunk", {"text": piece}, to=sid)
            sent = True

        if not sent:
            await sio.emit("bot_chunk", {"text": NO_INFO}, to=sid)

        await sio.emit("bot_done", {}, to=sid)

    return asgi_app
