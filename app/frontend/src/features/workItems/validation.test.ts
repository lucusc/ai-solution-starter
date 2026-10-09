import { describe, expect, it } from "vitest";

import { validatePdf } from "./validation";

describe("PDF validation", () => {
  it("accepts a bounded PDF", () => {
    const file = new File(["%PDF-1.4"], "synthetic.PDF", {
      type: "application/pdf",
    });
    expect(validatePdf(file)).toBeNull();
  });

  it.each([
    [new File(["text"], "synthetic.txt", { type: "text/plain" }), ".pdf"],
    [new File([], "synthetic.pdf", { type: "application/pdf" }), "empty"],
    [
      new File(["%PDF"], "synthetic.pdf", { type: "application/octet-stream" }),
      "application/pdf",
    ],
  ])("rejects invalid input", (file, message) => {
    expect(validatePdf(file)).toContain(message);
  });
});
