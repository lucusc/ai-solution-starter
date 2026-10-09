import { Button, Stack, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

export function NotFoundPage() {
  return (
    <Stack alignItems="flex-start" gap={2}>
      <Typography variant="h1">Page not found</Typography>
      <Typography color="text.secondary">
        The requested page does not exist in this starter application.
      </Typography>
      <Button component={RouterLink} to="/" variant="contained">
        Return to dashboard
      </Button>
    </Stack>
  );
}
