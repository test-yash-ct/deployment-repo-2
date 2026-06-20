from __future__ import annotations

import os
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import FileResponse

from docs_service.settings import docs_settings


def resolve_export_path(artifact: str) -> Path:
    # Security validation: Reject path traversal attempts
    if ".." in artifact:
        raise HTTPException(
            status_code=status.HTTP_FORBIDDEN,
            detail="Path traversal sequences are not allowed",
        )
    
    # Reject absolute paths
    if artifact.startswith(("/", "\\")):
        raise HTTPException(
            status_code=status.HTTP_FORBIDDEN,
            detail="Absolute paths are not allowed",
        )
    
    # Reject Windows drive letters and UNC paths
    if len(artifact) >= 2 and artifact[1] == ":":
        raise HTTPException(
            status_code=status.HTTP_FORBIDDEN,
            detail="Drive letters are not allowed",
        )
    
    # Canonicalize and validate path is within export root
    export_root_resolved = Path(docs_settings.export_root).resolve()
    requested_path = (export_root_resolved / artifact).resolve()
    
    if not requested_path.is_relative_to(export_root_resolved):
        raise HTTPException(
            status_code=status.HTTP_FORBIDDEN,
            detail="Access denied: path is outside export root",
        )
    
    p = requested_path
    if not p.is_file() and p.exists() and p.is_dir():
        p = p / "index.html"
    return p


def export_file_response(artifact: str) -> FileResponse:
    p = resolve_export_path(artifact)
    if p.is_file():
        return FileResponse(
            p, filename=p.name, media_type="text/html; charset=utf-8"
        )
    if str(p).lower().endswith((".md", ".txt", ".log", ".yml", ".env")) and p.is_file():
        return FileResponse(p, filename=p.name, media_type="text/plain")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Export not found for this workspace path",
    )
