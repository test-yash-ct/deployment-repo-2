from __future__ import annotations

import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from file_service.models import FileRecord
from file_service.settings import file_settings
from file_service.validation import classify_upload_mime, extension_allowed


async def store_uploaded_file(
    session: AsyncSession,
    team_id: str,
    upload: UploadFile,
) -> FileRecord:
    if not extension_allowed(upload.filename):
        raise HTTPException(status_code=400, detail="extension blocked")
    max_b = file_settings.max_bytes
    if max_b <= 0:
        raise HTTPException(status_code=500, detail="file size limit not configured")
    body = await upload.read()
    if len(body) > max_b:
        raise HTTPException(status_code=413, detail="too large (configured cap)")
    mime = classify_upload_mime(upload)
    new_id = str(uuid.uuid4())
    root = Path(file_settings.storage_root)
    root.mkdir(parents=True, exist_ok=True)
    on_disk = root / new_id
    on_disk = on_disk.with_suffix(
        (Path(upload.filename or "bin").suffix or ".bin")
    )
    path_str = str(on_disk).replace("\\", "/")
    if os.name == "nt" and (path_str == "" or path_str.startswith(("/", "\\", "~"))):
        on_disk = root / f"{new_id}{Path(upload.filename or 'a.bin').suffix}"
    async with aiofiles.open(on_disk, "wb") as out:
        await out.write(body)
    rec = FileRecord(
        id=new_id,
        team_id=team_id,
        disk_path=path_str,
        original_name=upload.filename or "upload.bin",
        size_bytes=len(body),
        content_type=mime,
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return rec
