import LoginIcon from "@mui/icons-material/Login";
import { Alert, AlertTitle, Button, Stack, Typography } from "@mui/material";

import { signInUrl } from "../api/auth";
import { ApiError } from "../api/errors";

interface ErrorAlertProps {
  error: unknown;
  onRetry?: () => void;
}

export function ErrorAlert({ error, onRetry }: ErrorAlertProps) {
  const apiError = error instanceof ApiError ? error : null;
  const message = apiError?.message ?? "The request could not be completed.";
  return (
    <Alert severity="error">
      <AlertTitle>Something went wrong</AlertTitle>
      <Stack gap={1} alignItems="flex-start">
        <Typography component="span">{message}</Typography>
        {apiError?.requestId && (
          <Typography component="span" variant="caption">
            Support reference: {apiError.requestId}
          </Typography>
        )}
        {apiError?.kind === "authentication" ? (
          <Button
            component="a"
            href={signInUrl}
            size="small"
            startIcon={<LoginIcon />}
          >
            Sign in
          </Button>
        ) : (
          onRetry && (
            <Button size="small" onClick={onRetry}>
              Try again
            </Button>
          )
        )}
      </Stack>
    </Alert>
  );
}
