import {
  AutoAwesomeOutlined,
  CloudUploadOutlined,
  FactCheckOutlined,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  Divider,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { useCallback, useEffect, useRef, useState } from "react";

import { listWorkItems } from "../api/workItems";
import { WorkItemForm } from "../features/workItems/WorkItemForm";
import { WorkItemList } from "../features/workItems/WorkItemList";
import type { WorkItem, WorkItemStatus } from "../types/workItems";

const steps = [
  {
    title: "Submit",
    text: "Upload one PDF through the authenticated backend API.",
    icon: <CloudUploadOutlined color="primary" />,
  },
  {
    title: "Process",
    text: "A workflow can read queued work and invoke the configured AI model.",
    icon: <AutoAwesomeOutlined color="primary" />,
  },
  {
    title: "Review",
    text: "Follow explicit lifecycle state and inspect structured output.",
    icon: <FactCheckOutlined color="primary" />,
  },
];

export function DashboardPage() {
  const [items, setItems] = useState<WorkItem[]>([]);
  const [status, setStatus] = useState<WorkItemStatus | "">("");
  const [continuationToken, setContinuationToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const fetchPage = useCallback(
    async (token?: string, append = false) => {
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      if (append) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }
      setError(null);
      try {
        const page = await listWorkItems({
          status: status || undefined,
          continuationToken: token,
          signal: controller.signal,
        });
        if (controllerRef.current !== controller) return;
        setItems((current) => (append ? [...current, ...page.items] : page.items));
        setContinuationToken(page.continuation_token);
      } catch (requestError) {
        if (
          !(requestError instanceof DOMException && requestError.name === "AbortError")
        ) {
          setError(requestError);
        }
      } finally {
        if (controllerRef.current === controller) {
          if (append) {
            setLoadingMore(false);
          } else {
            setLoading(false);
          }
        }
      }
    },
    [status],
  );

  const refresh = useCallback(
    () => void fetchPage(undefined, false),
    [fetchPage],
  );

  useEffect(() => {
    refresh();
    return () => controllerRef.current?.abort();
  }, [refresh]);

  return (
    <Stack gap={5}>
      <Box>
        <Typography variant="h1">A replaceable Azure AI application</Typography>
        <Typography color="text.secondary" fontSize="1.15rem" mt={1} maxWidth={760}>
          This hello-world flow demonstrates authenticated intake, durable state,
          workflow processing, and structured AI output without imposing a
          solution-specific domain.
        </Typography>
      </Box>

      <Stack direction={{ xs: "column", md: "row" }} gap={2}>
        {steps.map((step) => (
          <Card key={step.title} variant="outlined" sx={{ flex: 1 }}>
            <CardContent>
              <Stack direction="row" gap={1} alignItems="center">
                {step.icon}
                <Typography variant="h6">{step.title}</Typography>
              </Stack>
              <Typography color="text.secondary" mt={1}>
                {step.text}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Stack>

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Typography variant="h2">Create a work item</Typography>
        <Typography color="text.secondary" mt={0.5} mb={2.5}>
          Use a synthetic or non-sensitive PDF while evaluating the starter.
        </Typography>
        <WorkItemForm />
      </Paper>

      <Divider />

      <Box>
        <Typography variant="h2" mb={2}>
          Recent work items
        </Typography>
        <WorkItemList
          items={items}
          status={status}
          loading={loading}
          loadingMore={loadingMore}
          error={error}
          hasMore={continuationToken !== null}
          onStatusChange={setStatus}
          onRefresh={refresh}
          onLoadMore={() =>
            void fetchPage(continuationToken ?? undefined, true)
          }
        />
      </Box>
    </Stack>
  );
}
