import { useCallback, useEffect, useRef, useState } from "react";

import { ApiError } from "../../api/errors";
import { getWorkItem, getWorkItemStatus } from "../../api/workItems";
import type { WorkItem } from "../../types/workItems";

const NONTERMINAL = new Set(["submitted", "queued", "processing"]);
const POLL_INTERVAL_MS = 5_000;

export function useWorkItem(id: string) {
  const [item, setItem] = useState<WorkItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [pollError, setPollError] = useState<unknown>(null);
  const loadController = useRef<AbortController | null>(null);
  const pollController = useRef<AbortController | null>(null);
  const status = item?.status;

  const load = useCallback(
    async (showLoading = true) => {
      loadController.current?.abort();
      const controller = new AbortController();
      loadController.current = controller;
      if (showLoading) setLoading(true);
      setError(null);
      try {
        const result = await getWorkItem(id, controller.signal);
        if (loadController.current === controller) setItem(result);
      } catch (requestError) {
        if (
          loadController.current === controller &&
          !(requestError instanceof DOMException && requestError.name === "AbortError")
        ) {
          setError(requestError);
        }
      } finally {
        if (showLoading && loadController.current === controller) setLoading(false);
      }
    },
    [id],
  );

  useEffect(() => {
    void load();
    return () => loadController.current?.abort();
  }, [load]);

  useEffect(() => {
    if (!status || !NONTERMINAL.has(status)) return;
    let stopped = false;
    let timer: number | undefined;

    const schedule = () => {
      if (!stopped) timer = window.setTimeout(poll, POLL_INTERVAL_MS);
    };

    const poll = async () => {
      if (document.visibilityState === "hidden") {
        schedule();
        return;
      }
      const controller = new AbortController();
      pollController.current = controller;
      try {
        const status = await getWorkItemStatus(id, controller.signal);
        if (stopped) return;
        setPollError(null);
        if (NONTERMINAL.has(status.status)) {
          setItem((current) =>
            current
              ? {
                  ...current,
                  status: status.status,
                  updated_at: status.updated_at,
                  error: status.error,
                }
              : current,
          );
          schedule();
        } else {
          await load(false);
        }
      } catch (requestError) {
        if (stopped) return;
        if (
          requestError instanceof DOMException &&
          requestError.name === "AbortError"
        ) {
          return;
        }
        setPollError(requestError);
        if (
          requestError instanceof ApiError &&
          ["authentication", "not_found"].includes(requestError.kind)
        ) {
          return;
        }
        schedule();
      }
    };

    schedule();
    return () => {
      stopped = true;
      if (timer !== undefined) window.clearTimeout(timer);
      pollController.current?.abort();
    };
  }, [id, load, status]);

  return {
    item,
    loading,
    error,
    pollError,
    refresh: () => void load(),
  };
}
