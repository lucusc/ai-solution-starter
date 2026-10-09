import type { ApiErrorEnvelope } from "../types/api";
import { ApiError, type ApiFailureKind } from "./errors";

function failureKind(status: number): ApiFailureKind {
  if (status === 401) return "authentication";
  if (status === 404) return "not_found";
  if (status === 409) return "conflict";
  if ([400, 413, 415, 422].includes(status)) return "validation";
  if ([502, 503, 504].includes(status)) return "dependency";
  return "unexpected";
}

function isErrorEnvelope(value: unknown): value is ApiErrorEnvelope {
  if (!value || typeof value !== "object" || !("error" in value)) return false;
  const error = value.error;
  return (
    !!error &&
    typeof error === "object" &&
    "code" in error &&
    typeof error.code === "string" &&
    "message" in error &&
    typeof error.message === "string"
  );
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<{ data: T; response: Response }> {
  let response: Response;
  try {
    response = await fetch(path, {
      ...init,
      headers: {
        Accept: "application/json",
        ...init.headers,
      },
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(
      "The service could not be reached. Check your connection and try again.",
      "network",
      null,
      "network_error",
    );
  }

  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    if (isErrorEnvelope(body)) {
      throw new ApiError(
        body.error.message,
        failureKind(response.status),
        response.status,
        body.error.code,
        body.error.request_id,
      );
    }
    throw new ApiError(
      "The service returned an unexpected response.",
      failureKind(response.status),
      response.status,
      "unexpected_response",
      response.headers.get("X-Request-ID"),
    );
  }
  return { data: body as T, response };
}
