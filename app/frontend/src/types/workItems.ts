export const workItemStatuses = [
  "submitted",
  "queued",
  "processing",
  "completed",
  "failed",
] as const;

export type WorkItemStatus = (typeof workItemStatuses)[number];

export interface WorkItemSource {
  name: string;
  content_type: string;
  size_bytes: number;
  sha256: string;
}

export interface ProcessingError {
  code: string;
  message: string;
  retryable: boolean;
  occurred_at: string;
}

export interface WorkItem {
  id: string;
  created_at: string;
  updated_at: string;
  status: WorkItemStatus;
  version: number;
  source: WorkItemSource;
  result: Record<string, unknown> | null;
  error: ProcessingError | null;
}

export interface WorkItemStatusResponse {
  id: string;
  status: WorkItemStatus;
  updated_at: string;
  error: ProcessingError | null;
}

export interface WorkItemListResponse {
  items: WorkItem[];
  continuation_token: string | null;
}
