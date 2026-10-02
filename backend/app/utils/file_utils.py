"""
File validation and safe storage helpers.
"""

import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.config import settings


SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\- ]+")


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from a user-provided filename."""
    name = Path(filename).name  # strip any path components
    name = SAFE_FILENAME_RE.sub("", name).strip()
    return name or "resume"


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def validate_upload(file: UploadFile, content: bytes) -> str:
    """
    Validate uploaded resume file.

    Checks: presence, extension, emptiness, size limit.
    Returns sanitized filename or raises HTTPException.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided. Please choose a resume file.")

    ext = get_extension(file.filename)
    if ext not in settings.allowed_ext_list:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload a PDF or DOCX file.",
        )

    if not content or len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty. Please choose a valid resume.")

    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File is too large. Maximum size is {settings.max_file_size_mb} MB.",
        )

    # Basic magic-byte checks to reduce spoofed extensions
    if ext == ".pdf" and not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File does not appear to be a valid PDF.")
    if ext == ".docx" and not content.startswith(b"PK"):
        raise HTTPException(status_code=400, detail="File does not appear to be a valid DOCX.")

    return sanitize_filename(file.filename)


def build_storage_path(original_filename: str) -> tuple[str, Path]:
    """
    Create a unique file_id and destination path under the uploads folder.
    Returns (file_id, full_path).
    """
    ext = get_extension(original_filename)
    file_id = str(uuid.uuid4())
    safe_name = sanitize_filename(original_filename)
    # Store as: {file_id}__{safe_name}
    stored_name = f"{file_id}__{safe_name}"
    dest = Path(settings.upload_dir) / stored_name
    return file_id, dest


def resolve_upload_path(file_id: str) -> Path:
    """Find the stored file for a given file_id."""
    upload_dir = Path(settings.upload_dir)
    matches = list(upload_dir.glob(f"{file_id}__*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Uploaded resume not found. Please upload again.")
    return matches[0]


def original_filename_from_path(path: Path) -> str:
    """Extract the original filename portion from a stored path."""
    name = path.name
    if "__" in name:
        return name.split("__", 1)[1]
    return name
