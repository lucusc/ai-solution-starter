import { http, HttpResponse } from "msw";

import { queuedWorkItem } from "./fixtures";

export const handlers = [
  http.get("/.auth/me", () =>
    HttpResponse.json([{ user_name: "Starter User", identity_provider: "aad" }]),
  ),
  http.get("/api/v1/work-items", () =>
    HttpResponse.json({ items: [queuedWorkItem], continuation_token: null }),
  ),
  http.get("/api/v1/work-items/:id", () => HttpResponse.json(queuedWorkItem)),
  http.get("/api/v1/work-items/:id/status", () =>
    HttpResponse.json({
      id: queuedWorkItem.id,
      status: queuedWorkItem.status,
      updated_at: queuedWorkItem.updated_at,
      error: null,
    }),
  ),
  http.post("/api/v1/work-items", () =>
    HttpResponse.json(queuedWorkItem, { status: 201 }),
  ),
];
