import type { WorkItem } from "../types/workItems";

export const queuedWorkItem: WorkItem = {
  id: "11111111-1111-4111-8111-111111111111",
  created_at: "2026-01-01T12:00:00Z",
  updated_at: "2026-01-01T12:00:01Z",
  status: "queued",
  version: 2,
  source: {
    name: "synthetic.pdf",
    content_type: "application/pdf",
    size_bytes: 32,
    sha256: "a".repeat(64),
  },
  result: null,
  error: null,
};

export const completedWorkItem: WorkItem = {
  ...queuedWorkItem,
  id: "22222222-2222-4222-8222-222222222222",
  status: "completed",
  version: 4,
  updated_at: "2026-01-01T12:00:05Z",
  result: {
    summary: "A concise synthetic summary.",
    category: "example",
    confidence: 0.9,
  },
};

export const failedWorkItem: WorkItem = {
  ...queuedWorkItem,
  status: "failed",
  version: 3,
  error: {
    code: "processing_failed",
    message: "The synthetic item could not be processed.",
    retryable: false,
    occurred_at: "2026-01-01T12:00:05Z",
  },
};
