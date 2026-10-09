import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { server } from "../test/server";
import { queuedWorkItem } from "../test/fixtures";
import { createWorkItem, listWorkItems } from "./workItems";

describe("work-item API", () => {
  it("sends multipart content with an idempotency key", async () => {
    let contentType = "";
    let idempotencyKey = "";
    server.use(
      http.post("/api/v1/work-items", ({ request }) => {
        contentType = request.headers.get("content-type") ?? "";
        idempotencyKey = request.headers.get("idempotency-key") ?? "";
        expect(request.body).not.toBeNull();
        return HttpResponse.json(queuedWorkItem, {
          status: 200,
          headers: { "Idempotent-Replayed": "true" },
        });
      }),
    );
    const result = await createWorkItem(
      new File(["%PDF-1.4"], "synthetic.pdf", {
        type: "application/pdf",
      }),
      "request-key-123",
    );
    expect(contentType).toMatch(/^multipart\/form-data; boundary=/);
    expect(idempotencyKey).toBe("request-key-123");
    expect(result.replayed).toBe(true);
  });

  it("passes filters and opaque continuation tokens unchanged", async () => {
    let requestUrl = "";
    server.use(
      http.get("/api/v1/work-items", ({ request }) => {
        requestUrl = request.url;
        return HttpResponse.json({ items: [], continuation_token: null });
      }),
    );
    await listWorkItems({
      status: "processing",
      pageSize: 7,
      continuationToken: "opaque+/token==",
    });
    const query = new URL(requestUrl).searchParams;
    expect(query.get("status")).toBe("processing");
    expect(query.get("page_size")).toBe("7");
    expect(query.get("continuation_token")).toBe("opaque+/token==");
  });
});
