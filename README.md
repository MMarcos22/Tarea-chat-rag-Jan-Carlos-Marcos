# RAG + WebSockets + OpenAI + Nuxt 3 (sin pgvector)

Proyecto mínimo listo para probar:
- **Backend**: FastAPI + Socket.IO (ASGI), embeddings y chat con OpenAI, PostgreSQL (embeddings guardados como JSON, búsqueda en Python).
- **Frontend**: Nuxt 3 + socket.io-client, chat con streaming en tiempo real.
- **SQL**: esquema en `backend/db/schema_no_pgvector.sql` (no requiere pgvector).

## 1) Requisitos
- Python 3.10+
- PostgreSQL 13+
- Node.js 18+
- Una API key válida de OpenAI (ponla en `.env` del backend).

## 2) Base de datos
1. Crea la base en Postgres.
2. En **pgAdmin**, ejecuta `backend/db/schema_no_pgvector.sql`.

## 3) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tu DATABASE_URL y OPENAI_API_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 4) Frontend
```bash
cd frontend
npm install
npm run dev
```

Por defecto el frontend intenta conectarse a `http://localhost:8000`. Puedes ajustar en `nuxt.config.ts` con `NUXT_PUBLIC_API_BASE` y `NUXT_PUBLIC_WS_BASE`.

## 5) Uso
1. En la web, **sube un PDF**.
2. Espera a que procese (mensaje "Documento listo: ...").
3. Escribe preguntas en el chat.
4. Si no hay contexto relevante, el bot responde: **"No poseo información sobre ese tema en el documento cargado."**

## Notas
- Este proyecto NO guarda la clave en código; usa variables de entorno.
- Si crece el número de documentos, considera integrar `pgvector` o un vector store como FAISS/Chroma para acelerar las búsquedas.
