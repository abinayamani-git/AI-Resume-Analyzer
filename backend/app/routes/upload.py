"""Resume upload endpoint."""

from fastapi import APIRouter, File, UploadFile

from app.models import UploadResponse
from app.utils.file_utils import build_storage_path, validate_upload

router = APIRouter(tags=["upload"])


@router.post("/api/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Accept a PDF or DOCX resume, validate it, and store it locally.
    Returns a file_id used by /api/analyze.
    """
    content = await file.read()
    safe_name = validate_upload(file, content)
    file_id, dest = build_storage_path(safe_name)

    # Write to disk (local-only — not sent to third-party services)
    dest.write_bytes(content)

    return UploadResponse(
        file_id=file_id,
        filename=safe_name,
        message="Resume uploaded successfully",
        size_bytes=len(content),
    )
