from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from tempfile import SpooledTemporaryFile

from backend.models import StoredSource, WorkItemRecord, WorkItemStatus
from backend.pdf import ValidatedPdf


def pdf_bytes(label: str = "starter") -> bytes:
    return f"%PDF-1.4\n% {label}\n1 0 obj\n<<>>\nendobj\n%%EOF\n".encode()


def validated_pdf(filename: str = "example.pdf") -> ValidatedPdf:
    content = pdf_bytes()
    stream = SpooledTemporaryFile(max_size=1024, mode="w+b")
    stream.write(content)
    stream.seek(0)
    return ValidatedPdf(
        stream=stream,
        display_name=filename,
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
    )


def work_item(
    *,
    item_id: str = "6878c2f2-d19a-4fe7-a463-50b24d02518e",
    owner_id: str = "owner-1",
    status: WorkItemStatus = WorkItemStatus.QUEUED,
) -> WorkItemRecord:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return WorkItemRecord(
        id=item_id,
        created_at=now,
        updated_at=now,
        owner_id=owner_id,
        status=status,
        version=2,
        source_name="example.pdf",
        source=StoredSource(
            blob_name=f"work-items/{item_id}/source.pdf",
            size_bytes=10,
            sha256="a" * 64,
        ),
        idempotency_key_hash="b" * 64,
        etag="etag-2",
    )
