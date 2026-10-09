import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { renderWithProviders } from "../../test/render";
import { WorkItemResult } from "./WorkItemResult";

describe("WorkItemResult", () => {
  it("renders preferred fields and safe generic details", () => {
    renderWithProviders(
      <WorkItemResult
        result={{
          summary: "Synthetic summary",
          category: "example",
          nested: { enabled: true },
          markup: "<script>unsafe()</script>",
        }}
      />,
    );
    expect(screen.getByText("Synthetic summary")).toBeInTheDocument();
    expect(screen.getByText("example")).toBeInTheDocument();
    expect(screen.getByText("<script>unsafe()</script>")).toBeInTheDocument();
    expect(document.querySelector("script")).toBeNull();
  });
});
