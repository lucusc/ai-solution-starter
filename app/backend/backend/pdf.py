from __future__ import annotations

import asyncio
import hashlib
import re
from dataclasses import dataclass
from pathlib import PurePath
from tempfile import SpooledTemporaryFile
from typing import IO, cast

from werkzeug.datastructures import FileStorage

from .errors import RequestValidationError

PDF_SIGNATURE = b"%PDF-"
READ_CHUNK_SIZE = 64 * 1024
SPOOL_MEMORY_LIMIT = 1024 * 1024
MAX_DISPLAY_NAME_LENGTH = 180


@dataclass(slots=True)
class ValidatedPdf:
    stream: IO[bytes]
    display_name: str
    size_bytes: int
    sha256: str

    def close(self) -> None:
        self.stream.close()


def _display_name(filename: str) -> str:
    normalized = filename.replace("\\", "/")
    name = PurePath(normalized).name
    name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip()
    if not name or not name.lower().endswith(".pdf"):
        raise RequestValidationError(
            "invalid_pdf_filename", "The uploaded filename must end with .pdf."
        )
    stem = name[:-4].strip().rstrip(".")
    if not stem:
        raise RequestValidationError("invalid_pdf_filename", "The uploaded filename is invalid.")
    max_stem_length = MAX_DISPLAY_NAME_LENGTH - 4
    return f"{stem[:max_stem_length]}.pdf"


async def validate_pdf_upload(
    uploaded: FileStorage | None,
    *,
    max_size_bytes: int,
) -> ValidatedPdf:
    if uploaded is None or not uploaded.filename:
        raise RequestValidationError(
            "missing_pdf", "A PDF file is required in the file form field."
        )
    display_name = _display_name(uploaded.filename)
    content_type = (uploaded.content_type or "").split(";", 1)[0].strip().lower()
    if content_type != "application/pdf":
        raise RequestValidationError(
            "invalid_pdf_content_type",
            "The uploaded file must use the application/pdf content type.",
        )

    stream = SpooledTemporaryFile(max_size=SPOOL_MEMORY_LIMIT, mode="w+b")
    digest = hashlib.sha256()
    size = 0
    prefix = b""
    try:
        while True:
            chunk = await asyncio.to_thread(uploaded.stream.read, READ_CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
            if size > max_size_bytes:
                raise RequestValidationError(
                    "pdf_too_large",
                    "The uploaded PDF exceeds the maximum allowed size.",
                    status_code=413,
                )
            if len(prefix) < len(PDF_SIGNATURE):
                prefix += chunk[: len(PDF_SIGNATURE) - len(prefix)]
            digest.update(chunk)
            stream.write(chunk)
        if size == 0:
            raise RequestValidationError("empty_pdf", "The uploaded PDF is empty.")
        if prefix != PDF_SIGNATURE:
            raise RequestValidationError(
                "invalid_pdf_signature",
                "The uploaded file is not a valid PDF.",
            )
        stream.seek(0)
        return ValidatedPdf(
            stream=cast(IO[bytes], stream),
            display_name=display_name,
            size_bytes=size,
            sha256=digest.hexdigest(),
        )
    except Exception:
        stream.close()
        raise
