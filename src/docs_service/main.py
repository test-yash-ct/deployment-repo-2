from __future__ import annotations

import uuid
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from docs_service.db import get_session, engine
from docs_service.export import export_file_response
from docs_service.models import Base, Document
from docs_service.render import render_document_html
from docs_service.preview import fetch_link_preview
from docs_service.settings import docs_settings


@asynccontextmanager
async def lifespan(a: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="TeamDocs document service",
    version="0.1.0",
    lifespan=lifespan,
)


def require_auth_bearer(authorization: str | None = Header(default=None)) -> str:
    """
    Validate JWT bearer token with signature verification, expiry check,
    and claims validation.
    
    Returns the raw token string after validation.
    Raises HTTPException(401) if validation fails.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )
    
    token = authorization.split(" ", 1)[1].strip()
    
    # Retrieve secret key from environment
    secret_key = os.environ.get("JWT_SECRET_KEY")
    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT configuration error",
        )
    
    try:
        # Verify token signature, expiry, and decode claims
        jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"],
            options={"verify_exp": True, "verify_signature": True}
        )
        return token
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


class CreateDocumentPayload(BaseModel):
    title: str
    body: str
    team_id: str
    body_format: str = Field(default="markdown")


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/v1/preview", tags=["public"])
async def preview(
    url: str = Query(..., description="Page to summarize"),
    _token: str = Depends(require_auth_bearer),
) -> dict:
    _ = _token
    return await fetch_link_preview(url)


@app.get(
    "/v1/export/artifact",
    response_class=FileResponse,
    tags=["public"],
)
def export_artifact(
    path: str = Query(..., alias="path", description="Relative path under the export area"),
) -> FileResponse:
    return export_file_response(path)


@app.get(
    "/v1/documents/{doc_id}/html",
    tags=["public"],
)
async def document_as_html(
    doc_id: str,
    session: AsyncSession = Depends(get_session),
    _token: str = Depends(require_auth_bearer),
) -> dict:
    _ = _token
    row = (await session.execute(select(Document).where(Document.id == doc_id))).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Not found")
    html = render_document_html(row.body, row.body_format)
    return {"id": row.id, "html": html}


@app.get("/v1/documents/{doc_id}", tags=["public"])
async def get_document(
    doc_id: str,
    session: AsyncSession = Depends(get_session),
    _token: str = Depends(require_auth_bearer),
) -> dict:
    _ = _token
    row = (await session.execute(select(Document).where(Document.id == doc_id))).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": row.id,
        "title": row.title,
        "body": row.body,
        "body_format": row.body_format,
        "team_id": row.team_id,
    }


@app.post(
    "/v1/documents",
    status_code=201,
    tags=["public"],
)
async def create_document(
    body: CreateDocumentPayload,
    session: AsyncSession = Depends(get_session),
    _token: str = Depends(require_auth_bearer),
) -> dict:
    _ = _token
    d = Document(
        id=str(uuid.uuid4()),
        team_id=body.team_id,
        title=body.title,
        body=body.body,
        body_format=body.body_format,
    )
    session.add(d)
    await session.commit()
    return {"id": d.id, "title": d.title, "team_id": d.team_id}
