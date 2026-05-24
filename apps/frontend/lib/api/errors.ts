import type { AxiosError } from "axios";

export class ApiError extends Error {
  status: number | undefined;
  detail: string;
  raw: unknown;

  constructor(status: number | undefined, detail: string, raw: unknown) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.raw = raw;
  }
}

/** Turn any AxiosError / unknown error into a human-readable string. */
export function extractDetail(error: unknown): string {
  if (error instanceof ApiError) return error.detail;
  const ax = error as AxiosError<{ detail?: unknown }> | undefined;
  if (ax?.response) {
    const data = ax.response.data;
    if (typeof data === "string") return data;
    if (data && typeof data === "object" && "detail" in data) {
      const detail = (data as { detail?: unknown }).detail;
      if (typeof detail === "string") return detail;
      // FastAPI 422 returns detail as an array of validation errors
      if (Array.isArray(detail)) {
        return detail
          .map((d) => {
            if (d && typeof d === "object" && "msg" in d) {
              return String((d as { msg: unknown }).msg);
            }
            return JSON.stringify(d);
          })
          .join("; ");
      }
    }
    return `${ax.response.status} ${ax.response.statusText ?? ""}`.trim();
  }
  if (error instanceof Error) return error.message;
  return "Unknown error";
}

/** Normalize an axios error into an ApiError. Used by interceptors. */
export function toApiError(error: unknown): ApiError {
  const ax = error as AxiosError | undefined;
  return new ApiError(ax?.response?.status, extractDetail(error), error);
}
