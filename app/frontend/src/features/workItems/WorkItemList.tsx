import RefreshOutlined from "@mui/icons-material/RefreshOutlined";
import {
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";

import { ErrorAlert } from "../../components/ErrorAlert";
import { LoadingState } from "../../components/LoadingState";
import { StatusChip } from "../../components/StatusChip";
import {
  workItemStatuses,
  type WorkItem,
  type WorkItemStatus,
} from "../../types/workItems";
import { formatDate } from "../../utils/dates";

interface WorkItemListProps {
  items: WorkItem[];
  status: WorkItemStatus | "";
  loading: boolean;
  loadingMore: boolean;
  error: unknown;
  hasMore: boolean;
  onStatusChange: (status: WorkItemStatus | "") => void;
  onRefresh: () => void;
  onLoadMore: () => void;
}

export function WorkItemList({
  items,
  status,
  loading,
  loadingMore,
  error,
  hasMore,
  onStatusChange,
  onRefresh,
  onLoadMore,
}: WorkItemListProps) {
  return (
    <Stack gap={2}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        gap={2}
        justifyContent="space-between"
      >
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel id="status-filter-label">Status</InputLabel>
          <Select
            labelId="status-filter-label"
            label="Status"
            value={status}
            onChange={(event) =>
              onStatusChange(event.target.value as WorkItemStatus | "")
            }
          >
            <MenuItem value="">All statuses</MenuItem>
            {workItemStatuses.map((value) => (
              <MenuItem key={value} value={value}>
                {value[0].toUpperCase() + value.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button
          startIcon={<RefreshOutlined />}
          onClick={onRefresh}
          disabled={loading}
        >
          Refresh
        </Button>
      </Stack>

      {loading ? (
        <LoadingState label="Loading work items" />
      ) : error ? (
        <ErrorAlert error={error} onRetry={onRefresh} />
      ) : items.length === 0 ? (
        <Box textAlign="center" py={5}>
          <Typography variant="h6">No work items yet</Typography>
          <Typography color="text.secondary">
            Submit a PDF to exercise the starter application flow.
          </Typography>
        </Box>
      ) : (
        <Stack gap={1.5}>
          {items.map((item) => (
            <Card key={item.id} variant="outlined">
              <CardActionArea
                component={RouterLink}
                to={`/work-items/${item.id}`}
              >
                <CardContent>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    gap={1.5}
                    alignItems={{ sm: "center" }}
                  >
                    <Box flexGrow={1} minWidth={0}>
                      <Typography fontWeight={600} noWrap>
                        {item.source.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Created {formatDate(item.created_at)} · Updated{" "}
                        {formatDate(item.updated_at)}
                      </Typography>
                    </Box>
                    <StatusChip status={item.status} />
                  </Stack>
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Stack>
      )}
      {hasMore && !loading && (
        <Button onClick={onLoadMore} disabled={loadingMore}>
          {loadingMore ? "Loading…" : "Load more"}
        </Button>
      )}
    </Stack>
  );
}
