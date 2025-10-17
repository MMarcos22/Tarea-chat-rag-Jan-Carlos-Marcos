RAG + WebSockets + OpenAI + Nuxt 

Proyecto:
- **Backend**: FastAPI + Socket.IO (ASGI), embeddings y chat con OpenAI, PostgreSQL.
- **Frontend**: Nuxt 3 + socket.io-client, chat con streaming en tiempo real.
- **SQL**.

Requisitos
- Python 3.10+
- PostgreSQL 13+
- Node.js 18+
- Una API key válida de OpenAI (ponla en `.env` del backend).

Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tu DATABASE_URL y OPENAI_API_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend
```bash
cd frontend
npm install
npm run dev
```

Por defecto el frontend intenta conectarse a `http://localhost:8000`. Puedes ajustar en `nuxt.config.ts` con `NUXT_PUBLIC_API_BASE` y `NUXT_PUBLIC_WS_BASE`.

Uso
1. En la web, **sube un PDF**.
2. Espera a que procese (mensaje "Documento listo: ...").
3. Escribe preguntas en el chat.
4. Si no hay contexto relevante, el bot responde: **"No poseo información sobre ese tema en el documento cargado."**


