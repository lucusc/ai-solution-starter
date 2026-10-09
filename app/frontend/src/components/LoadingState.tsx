import { CircularProgress, Stack, Typography } from "@mui/material";

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <Stack alignItems="center" gap={1.5} py={5} role="status">
      <CircularProgress size={28} />
      <Typography color="text.secondary">{label}</Typography>
    </Stack>
  );
}
