import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { renderWithProviders } from "../test/render";
import { AppShell } from "./AppShell";

describe("AppShell", () => {
  it("shows the Easy Auth account and sign-out control", async () => {
    renderWithProviders(
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<div>Dashboard</div>} />
        </Route>
      </Routes>,
    );
    expect(await screen.findByText("Starter User")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Sign out" })).toHaveAttribute(
      "href",
      "/.auth/logout?post_logout_redirect_uri=/",
    );
  });
});
