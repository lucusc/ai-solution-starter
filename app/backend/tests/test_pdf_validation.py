from io import BytesIO

import pytest
from backend.errors import RequestValidationError
from backend.pdf import validate_pdf_upload
from werkzeug.datastructures import FileStorage

from tests.helpers import pdf_bytes


@pytest.mark.asyncio
async def test_valid_pdf_is_spooled_and_hashed() -> None:
    upload = FileStorage(
        stream=BytesIO(pdf_bytes()),
        filename="../../Example.PDF",
        content_type="application/pdf",
    )
    validated = await validate_pdf_upload(upload, max_size_bytes=1024)
    try:
        assert validated.display_name == "Example.pdf"
        assert validated.stream.read().startswith(b"%PDF-")
        assert len(validated.sha256) == 64
    finally:
        validated.close()


@pytest.mark.asyncio
async def test_invalid_signature_is_rejected() -> None:
    upload = FileStorage(
        stream=BytesIO(b"not a pdf"),
        filename="example.pdf",
        content_type="application/pdf",
    )
    with pytest.raises(RequestValidationError) as raised:
        await validate_pdf_upload(upload, max_size_bytes=1024)
    assert raised.value.code == "invalid_pdf_signature"


@pytest.mark.asyncio
async def test_oversized_pdf_is_rejected() -> None:
    upload = FileStorage(
        stream=BytesIO(b"%PDF-" + b"x" * 20),
        filename="example.pdf",
        content_type="application/pdf",
    )
    with pytest.raises(RequestValidationError) as raised:
        await validate_pdf_upload(upload, max_size_bytes=10)
    assert raised.value.status_code == 413
