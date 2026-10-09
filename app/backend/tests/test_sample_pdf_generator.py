from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_sample_pdf import build_sample_pdf, write_sample_pdf


def test_sample_pdf_is_deterministic_and_valid() -> None:
    first = build_sample_pdf()
    second = build_sample_pdf()

    assert first == second
    assert first.startswith(b"%PDF-1.4")
    assert first.endswith(b"%%EOF\n")
    assert 0 < len(first) < 20 * 1024 * 1024
    assert b"Fictional example for local validation only." in first


def test_write_sample_pdf_refuses_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "sample.pdf"
    size, digest = write_sample_pdf(output)

    assert size == output.stat().st_size
    assert len(digest) == 64
    with pytest.raises(FileExistsError):
        write_sample_pdf(output)


def test_write_sample_pdf_allows_explicit_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "sample.pdf"
    write_sample_pdf(output)
    original = output.read_bytes()
    size, _ = write_sample_pdf(output, overwrite=True)

    assert output.read_bytes() == original
    assert size == len(original)
