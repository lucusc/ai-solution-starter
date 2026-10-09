const MAX_PDF_SIZE_BYTES = 20 * 1024 * 1024;

export function validatePdf(file: File | null): string | null {
  if (!file) return "Choose a PDF to submit.";
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    return "The selected file must use a .pdf extension.";
  }
  if (file.type && file.type !== "application/pdf") {
    return "The selected file must be reported as application/pdf.";
  }
  if (file.size === 0) return "The selected PDF is empty.";
  if (file.size > MAX_PDF_SIZE_BYTES) {
    return "The selected PDF must be 20 MB or smaller.";
  }
  return null;
}
