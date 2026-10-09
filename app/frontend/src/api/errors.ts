export type ApiFailureKind =
  | "authentication"
  | "not_found"
  | "validation"
  | "conflict"
  | "dependency"
  | "network"
  | "unexpected";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly kind: ApiFailureKind,
    readonly status: number | null,
    readonly code: string,
    readonly requestId: string | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
