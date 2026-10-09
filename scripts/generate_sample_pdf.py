#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

SAMPLE_LINES = (
    "AI Solution Starter - Synthetic Work Item",
    "Fictional example for local validation only.",
    "Request: Prepare a concise onboarding checklist for a new project team.",
    "Priority: Standard.",
    "Audience: Engineers and project stakeholders.",
    "Outcome: Summarize the request, classify it, and identify key points.",
)


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_sample_pdf() -> bytes:
    text_commands = ["BT", "/F1 14 Tf", "72 720 Td"]
    for index, line in enumerate(SAMPLE_LINES):
        if index:
            text_commands.append("0 -28 Td")
        text_commands.append(f"({_escape_pdf_text(line)}) Tj")
    text_commands.append("ET")
    stream = ("\n".join(text_commands) + "\n").encode("ascii")

    objects = (
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(stream)).encode("ascii")
        + b" >>\nstream\n"
        + stream
        + b"endstream",
    )

    content = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(content))
        content.extend(f"{number} 0 obj\n".encode("ascii"))
        content.extend(body)
        content.extend(b"\nendobj\n")

    xref_offset = len(content)
    content.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    content.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    content.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(content)


def write_sample_pdf(output: Path, *, overwrite: bool = False) -> tuple[int, str]:
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    content = build_sample_pdf()
    output.write_bytes(content)
    return len(content), hashlib.sha256(content).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the deterministic starter PDF.")
    parser.add_argument("output", type=Path, help="Output PDF path.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output when it already exists.",
    )
    args = parser.parse_args()

    try:
        size, digest = write_sample_pdf(args.output, overwrite=args.overwrite)
    except FileExistsError as exc:
        parser.error(str(exc))
    print(f"Generated {args.output} ({size} bytes, sha256={digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
