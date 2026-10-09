import { act, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { completedWorkItem, queuedWorkItem } from "../test/fixtures";
import { renderWithProviders } from "../test/render";
import { server } from "../test/server";
import { WorkItemDetailPage } from "./WorkItemDetailPage";

describe("WorkItemDetailPage", () => {
  afterEach(() => vi.useRealTimers());

  it("polls a nonterminal item and loads its completed result", async () => {
    let detailCalls = 0;
    server.use(
      http.get("/api/v1/work-items/:id", () => {
        detailCalls += 1;
        return HttpResponse.json(
          detailCalls === 1 ? queuedWorkItem : completedWorkItem,
        );
      }),
      http.get("/api/v1/work-items/:id/status", () =>
        HttpResponse.json({
          id: queuedWorkItem.id,
          status: "completed",
          updated_at: completedWorkItem.updated_at,
          error: null,
        }),
      ),
    );
    vi.useFakeTimers({ shouldAdvanceTime: true });
    renderWithProviders(
      <Routes>
        <Route path="/work-items/:id" element={<WorkItemDetailPage />} />
      </Routes>,
      [`/work-items/${queuedWorkItem.id}`],
    );
    expect(await screen.findByText("Queued")).toBeInTheDocument();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(5_000);
    });
    expect(
      await screen.findByText("A concise synthetic summary."),
    ).toBeInTheDocument();
    expect(detailCalls).toBe(2);
  });
});
