import { fireEvent, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { queuedWorkItem } from "../../test/fixtures";
import { renderWithProviders } from "../../test/render";
import { server } from "../../test/server";
import { WorkItemForm } from "./WorkItemForm";

describe("WorkItemForm", () => {
  it("reuses the idempotency key after an ambiguous network failure", async () => {
    const keys: string[] = [];
    let attempts = 0;
    server.use(
      http.post("/api/v1/work-items", ({ request }) => {
        keys.push(request.headers.get("idempotency-key") ?? "");
        attempts += 1;
        if (attempts === 1) return HttpResponse.error();
        return HttpResponse.json(queuedWorkItem, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    const { container } = renderWithProviders(
      <Routes>
        <Route path="/" element={<WorkItemForm />} />
        <Route path="/work-items/:id" element={<div>Detail opened</div>} />
      </Routes>,
    );
    const input = container.querySelector('input[type="file"]');
    expect(input).not.toBeNull();
    fireEvent.change(input!, {
      target: {
        files: [
          new File(["%PDF-1.4"], "synthetic.pdf", {
            type: "application/pdf",
          }),
        ],
      },
    });
    await user.click(screen.getByRole("button", { name: "Create work item" }));
    await user.click(await screen.findByRole("button", { name: "Try again" }));
    expect(await screen.findByText("Detail opened")).toBeInTheDocument();
    await waitFor(() => expect(keys).toHaveLength(2));
    expect(keys[0]).toBeTruthy();
    expect(keys[1]).toBe(keys[0]);
  });
});
