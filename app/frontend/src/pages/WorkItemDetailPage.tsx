import ArrowBackOutlined from "@mui/icons-material/ArrowBackOutlined";
import RefreshOutlined from "@mui/icons-material/RefreshOutlined";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useLocation, useParams } from "react-router-dom";

import { ErrorAlert } from "../components/ErrorAlert";
import { LoadingState } from "../components/LoadingState";
import { StatusChip } from "../components/StatusChip";
import { WorkItemResult } from "../features/workItems/WorkItemResult";
import { useWorkItem } from "../features/workItems/useWorkItem";
import { formatDate } from "../utils/dates";
import { formatFileSize } from "../utils/files";

export function WorkItemDetailPage() {
  const { id = "" } = useParams();
  const location = useLocation();
  const { item, loading, error, pollError, refresh } = useWorkItem(id);
  const replayed = Boolean(
    location.state &&
      typeof location.state === "object" &&
      "replayed" in location.state &&
      location.state.replayed,
  );

  if (loading) return <LoadingState label="Loading work item" />;
  if (error || !item) return <ErrorAlert error={error} onRetry={refresh} />;

  return (
    <Stack gap={3}>
      <Box>
        <Button
          component={RouterLink}
          to="/"
          startIcon={<ArrowBackOutlined />}
          sx={{ mb: 1 }}
        >
          Back to dashboard
        </Button>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          gap={2}
          alignItems={{ sm: "center" }}
        >
          <Box flexGrow={1} minWidth={0}>
            <Typography variant="h1" fontSize="clamp(1.7rem, 4vw, 2.5rem)">
              {item.source.name}
            </Typography>
            <Typography color="text.secondary">
              Created {formatDate(item.created_at)}
            </Typography>
          </Box>
          <StatusChip status={item.status} />
          <Button startIcon={<RefreshOutlined />} onClick={refresh}>
            Refresh
          </Button>
        </Stack>
      </Box>

      {replayed && (
        <Alert severity="info">
          The previous submission was recovered using its idempotency key.
        </Alert>
      )}
      {pollError !== null && (
        <Alert severity="warning">
          Automatic status refresh is temporarily unavailable. You can refresh
          manually.
        </Alert>
      )}

      <Card variant="outlined">
        <CardContent>
          <Stack gap={2}>
            <Typography variant="h6">Source</Typography>
            <Stack direction={{ xs: "column", sm: "row" }} gap={3}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Type
                </Typography>
                <Typography>{item.source.content_type}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Size
                </Typography>
                <Typography>{formatFileSize(item.source.size_bytes)}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Updated
                </Typography>
                <Typography>{formatDate(item.updated_at)}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Version
                </Typography>
                <Typography>{item.version}</Typography>
              </Box>
            </Stack>
            <Divider />
            <details>
              <summary>Technical details</summary>
              <Typography
                component="code"
                variant="body2"
                sx={{ overflowWrap: "anywhere" }}
              >
                SHA-256: {item.source.sha256}
              </Typography>
            </details>
          </Stack>
        </CardContent>
      </Card>

      {["submitted", "queued", "processing"].includes(item.status) && (
        <Alert severity="info" aria-live="polite">
          This work item is {item.status}. This page checks for updates every five
          seconds while it is open.
        </Alert>
      )}

      {item.status === "completed" && item.result && (
        <Card variant="outlined">
          <CardContent>
            <WorkItemResult result={item.result} />
          </CardContent>
        </Card>
      )}

      {item.status === "failed" && item.error && (
        <Alert severity="error">
          <Stack gap={0.5}>
            <Typography fontWeight={700}>{item.error.message}</Typography>
            <Stack direction="row" gap={1} alignItems="center">
              <Chip label={item.error.code} size="small" />
              <Typography variant="caption">
                {item.error.retryable ? "Retryable failure" : "Terminal failure"} ·{" "}
                {formatDate(item.error.occurred_at)}
              </Typography>
            </Stack>
          </Stack>
        </Alert>
      )}
    </Stack>
  );
}
