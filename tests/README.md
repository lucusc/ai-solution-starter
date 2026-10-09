# Tests

This directory contains cross-component fixtures and generated sample
boundaries.

Component-specific tests should remain close to their application component
when the selected framework supports that convention.

`sample-data/generated/` is ignored. Generate the starter PDF with:

```bash
.venv/bin/python scripts/generate_sample_pdf.py \
  tests/sample-data/generated/hello-world.pdf
```
