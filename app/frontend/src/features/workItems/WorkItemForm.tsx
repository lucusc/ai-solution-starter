import CloudUploadOutlined from "@mui/icons-material/CloudUploadOutlined";
import {
  Alert,
  Box,
  Button,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import { type ChangeEvent, type FormEvent, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { createWorkItem } from "../../api/workItems";
import { ErrorAlert } from "../../components/ErrorAlert";
import { formatFileSize } from "../../utils/files";
import { validatePdf } from "./validation";

export function WorkItemForm() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const idempotencyKeyRef = useRef<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<unknown>(null);
  const [submitting, setSubmitting] = useState(false);

  function selectFile(selected: File | null) {
    setFile(selected);
    setValidationError(validatePdf(selected));
    setSubmitError(null);
    idempotencyKeyRef.current = null;
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0] ?? null);
  }

  async function submitSelectedFile() {
    const error = validatePdf(file);
    setValidationError(error);
    if (error || !file || submitting) return;

    idempotencyKeyRef.current ??= crypto.randomUUID();
    setSubmitting(true);
    setSubmitError(null);
    try {
      const result = await createWorkItem(file, idempotencyKeyRef.current);
      idempotencyKeyRef.current = null;
      navigate(`/work-items/${result.item.id}`, {
        state: { replayed: result.replayed },
      });
    } catch (requestError) {
      setSubmitError(requestError);
    } finally {
      setSubmitting(false);
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void submitSelectedFile();
  }

  return (
    <Box component="form" onSubmit={onSubmit} noValidate>
      <Stack gap={2}>
        <Box
          sx={{
            border: "2px dashed",
            borderColor: validationError ? "error.main" : "divider",
            borderRadius: 2,
            p: 3,
            textAlign: "center",
            bgcolor: "background.default",
          }}
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault();
            selectFile(event.dataTransfer.files[0] ?? null);
          }}
        >
          <input
            ref={inputRef}
            hidden
            type="file"
            accept=".pdf,application/pdf"
            onChange={onFileChange}
            aria-describedby="pdf-help"
          />
          <CloudUploadOutlined color="primary" sx={{ fontSize: 40 }} />
          <Typography fontWeight={600} mt={1}>
            Choose a PDF or drop it here
          </Typography>
          <Typography id="pdf-help" color="text.secondary" variant="body2">
            One PDF, up to 20 MB. The backend performs final validation.
          </Typography>
          <Button
            sx={{ mt: 2 }}
            variant="outlined"
            onClick={() => inputRef.current?.click()}
          >
            Select PDF
          </Button>
          {file && (
            <Typography mt={2} variant="body2">
              {file.name} · {formatFileSize(file.size)}
            </Typography>
          )}
        </Box>
        {validationError && <Alert severity="warning">{validationError}</Alert>}
        {submitError !== null && (
          <ErrorAlert
            error={submitError}
            onRetry={() => void submitSelectedFile()}
          />
        )}
        {submitting && <LinearProgress aria-label="Submitting PDF" />}
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={submitting || !file}
        >
          {submitting ? "Submitting…" : "Create work item"}
        </Button>
      </Stack>
    </Box>
  );
}
