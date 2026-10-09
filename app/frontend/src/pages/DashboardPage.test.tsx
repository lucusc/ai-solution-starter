import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { completedWorkItem, queuedWorkItem } from "../test/fixtures";
import { renderWithProviders } from "../test/render";
import { server } from "../test/server";
import { DashboardPage } from "./DashboardPage";

describe("DashboardPage", () => {
  it("filters and appends continuation pages", async () => {
    const requests: string[] = [];
    server.use(
      http.get("/api/v1/work-items", ({ request }) => {
        const url = new URL(request.url);
        requests.push(url.search);
        if (url.searchParams.get("continuation_token")) {
          return HttpResponse.json({
            items: [completedWorkItem],
            continuation_token: null,
          });
        }
        return HttpResponse.json({
          items: [queuedWorkItem],
          continuation_token: "next-token",
        });
      }),
    );
    const user = userEvent.setup();
    renderWithProviders(<DashboardPage />);
    expect(await screen.findByText("synthetic.pdf")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Load more" }));
    await waitFor(() =>
      expect(screen.getAllByText("synthetic.pdf")).toHaveLength(2),
    );
    await user.click(screen.getByLabelText("Status"));
    await user.click(screen.getByRole("option", { name: "Processing" }));
    await waitFor(() =>
      expect(
        requests.some((query) => query.includes("status=processing")),
      ).toBe(true),
    );
  });
});
