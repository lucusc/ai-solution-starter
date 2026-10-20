# Synthetic sample data

Generate the hello-world PDF from the repository root:

```bash
.venv/bin/python scripts/generate_sample_pdf.py \
  tests/sample-data/generated/hello-world.pdf
```

The generated directory is ignored. Do not commit generated PDFs or replace
this sample with a real document.

The generator prints the byte count and SHA-256. Re-running without
`--overwrite` refuses an existing destination; add that flag only when
intentionally replacing the synthetic output. Use the same fixed content for
repeatable tests, not as proof that arbitrary or near-limit PDFs process
successfully in Azure.
