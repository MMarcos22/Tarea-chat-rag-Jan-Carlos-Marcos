from uuid import UUID
from typing import Iterable, Optional

import psycopg2
from psycopg2.extras import Json  # 👈 para insertar jsonb correctamente
from .connection import get_conn


class PgDocumentRepository:
    def save_pdf(
        self, *,
        title: str,
        filename: str,
        mime_type: str,
        file_bytes: bytes,
        owner_id: Optional[UUID]
    ):
        sql = '''
        INSERT INTO rag.document (title, filename, mime_type, file_size_bytes, file_data)
        VALUES (%s,%s,%s,%s,%s) RETURNING id;
        '''
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (title, filename, mime_type, len(file_bytes), psycopg2.Binary(file_bytes)))
            doc_id = cur.fetchone()[0]
        return doc_id

    def add_chunks(self, document_id: UUID, chunks: Iterable[dict]) -> list[UUID]:
        sql = '''
        INSERT INTO rag.document_chunk (document_id, chunk_index, content)
        VALUES (%s,%s,%s) RETURNING id;
        '''
        ids: list[UUID] = []
        with get_conn() as conn, conn.cursor() as cur:
            for c in chunks:
                cur.execute(sql, (str(document_id), c["chunk_index"], c["content"]))
                ids.append(cur.fetchone()[0])
            conn.commit()
        return ids

    def get_document(self, document_id: UUID) -> dict:
        sql = "SELECT id, title, filename, mime_type, file_size_bytes FROM rag.document WHERE id=%s"
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (str(document_id),))
            row = cur.fetchone()
        if not row:
            raise ValueError("Documento no encontrado")
        return {
            "id": row[0],
            "title": row[1],
            "filename": row[2],
            "mime_type": row[3],
            "file_size_bytes": row[4],
        }


class JsonVectorRepository:
    def upsert_embeddings(self, pairs: Iterable[tuple[UUID, list[float]]]) -> None:
        """
        Guarda embeddings como JSONB (no como string JSON).
        """
        sql = '''
        INSERT INTO rag.document_chunk_embedding (chunk_id, embedding)
        VALUES (%s, %s)
        ON CONFLICT (chunk_id) DO UPDATE SET embedding = EXCLUDED.embedding;
        '''
        with get_conn() as conn, conn.cursor() as cur:
            for chunk_id, vec in pairs:
                # 👇 Json(vec) hace que psycopg2 lo envíe como jsonb nativo
                cur.execute(sql, (str(chunk_id), Json(vec)))
            conn.commit()

    def search(self, query_embedding: list[float], top_k: int, document_id: UUID):
        import numpy as np
        q = np.array(query_embedding, dtype=float)

        sql = '''
        SELECT c.id, c.document_id, c.chunk_index, c.content, e.embedding
        FROM rag.document_chunk c
        JOIN rag.document_chunk_embedding e ON e.chunk_id = c.id
        WHERE c.document_id = %s;
        '''
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, (str(document_id),))
            rows = cur.fetchall()

        scored = []
        for r in rows:
            val = r[4]
            # Puede venir como list (jsonb decodificado) o como string JSON si quedó antiguo
            if isinstance(val, (list, tuple, np.ndarray)):
                emb = np.array(val, dtype=float)
            else:
                # fallback por si algún registro viejo quedó como texto JSON
                import json as _json
                emb = np.array(_json.loads(val), dtype=float)

            # coseno con protección por si hay norma cero
            denom = (np.linalg.norm(q) * np.linalg.norm(emb))
            sim = float(np.dot(q, emb) / denom) if denom else 0.0

            scored.append({
                "chunk_id": r[0],
                "document_id": r[1],
                "chunk_index": r[2],
                "content": r[3],
                "score": sim
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:max(1, top_k)]
