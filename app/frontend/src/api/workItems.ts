import type {
  WorkItem,
  WorkItemListResponse,
  WorkItemStatus,
  WorkItemStatusResponse,
} from "../types/workItems";
import { apiRequest } from "./client";

export interface ListWorkItemsOptions {
  status?: WorkItemStatus;
  pageSize?: number;
  continuationToken?: string;
  signal?: AbortSignal;
}

export async function createWorkItem(
  file: File,
  idempotencyKey: string,
  signal?: AbortSignal,
): Promise<{ item: WorkItem; replayed: boolean }> {
  const formData = new FormData();
  formData.append("file", file);
  const { data, response } = await apiRequest<WorkItem>("/api/v1/work-items", {
    method: "POST",
    body: formData,
    signal,
    headers: { "Idempotency-Key": idempotencyKey },
  });
  return {
    item: data,
    replayed: response.headers.get("Idempotent-Replayed") === "true",
  };
}

export async function listWorkItems({
  status,
  pageSize = 20,
  continuationToken,
  signal,
}: ListWorkItemsOptions = {}): Promise<WorkItemListResponse> {
  const query = new URLSearchParams({ page_size: String(pageSize) });
  if (status) query.set("status", status);
  if (continuationToken) query.set("continuation_token", continuationToken);
  const { data } = await apiRequest<WorkItemListResponse>(
    `/api/v1/work-items?${query.toString()}`,
    { signal },
  );
  return data;
}

export async function getWorkItem(
  id: string,
  signal?: AbortSignal,
): Promise<WorkItem> {
  const { data } = await apiRequest<WorkItem>(
    `/api/v1/work-items/${encodeURIComponent(id)}`,
    { signal },
  );
  return data;
}

export async function getWorkItemStatus(
  id: string,
  signal?: AbortSignal,
): Promise<WorkItemStatusResponse> {
  const { data } = await apiRequest<WorkItemStatusResponse>(
    `/api/v1/work-items/${encodeURIComponent(id)}/status`,
    { signal },
  );
  return data;
}
