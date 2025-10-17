from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from app.application.use_cases.UploadDocumentUseCase import UploadDocumentUseCase
import logging, traceback

def build_routes(upload_uc: UploadDocumentUseCase) -> APIRouter:
    """
    Router HTTP que inyecta UploadDocumentUseCase desde main.py.
    Requiere owner_id -> se toma de X-User-Id o se usa 'anon'.
    """
    router = APIRouter(prefix="/api/v1", tags=["documents"])

    @router.get("/health")
    async def health():
        return {"ok": True}

    @router.post("/documents")
    async def upload_pdf(
        request: Request,
        file: UploadFile = File(...),
        title: str | None = Form(None),
    ):
        try:
            if not file:
                raise HTTPException(status_code=400, detail="Falta archivo")

            content = await file.read()

            # 1) Resolvemos owner_id
            owner_id = request.headers.get("X-User-Id") or "anon"

            # 2) Ejecutamos caso de uso con owner_id requerido
            doc_id = upload_uc.execute(
                file_bytes=content,
                filename=file.filename or "document.pdf",
                mime_type=file.content_type or "application/pdf",
                title=title or (file.filename or "documento"),
                owner_id=owner_id,             # <--- clave
            )

            return JSONResponse(status_code=200, content={"document_id": str(doc_id)})

        except HTTPException:
            raise
        except Exception as e:
            logging.error("Error en /documents: %s", e)
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"error": str(e), "type": e.__class__.__name__},
            )

    return router
