"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { ApiError, extractDetail } from "@/lib/api/errors";

export interface UseApiOptions {
  /** Skip the fetch entirely (e.g. while userId is null). Default true. */
  enabled?: boolean;
  /** Refetch whenever any of these change. */
  deps?: ReadonlyArray<unknown>;
  /** Show a toast on error. Default true. */
  toastOnError?: boolean;
  /** Override the toast prefix. */
  toastPrefix?: string;
}

export interface UseApiResult<T> {
  data: T | undefined;
  error: ApiError | undefined;
  loading: boolean;
  refetch: () => Promise<void>;
}

/**
 * Generic data hook with AbortController + toast-on-error. Suppresses 401s
 * because the axios interceptor already handled them by calling `handle401()`.
 */
export function useApi<T>(
  fn: (signal: AbortSignal) => Promise<T>,
  opts: UseApiOptions = {},
): UseApiResult<T> {
  const { enabled = true, deps = [], toastOnError = true, toastPrefix } = opts;

  const [data, setData] = useState<T | undefined>(undefined);
  const [error, setError] = useState<ApiError | undefined>(undefined);
  const [loading, setLoading] = useState<boolean>(enabled);

  // Keep latest fn/opts in refs so refetch always uses fresh closures.
  // Mutating refs inside useEffect (not during render) avoids the React 19
  // "refs during render" warning.
  const fnRef = useRef(fn);
  const optsRef = useRef({ toastOnError, toastPrefix });
  useEffect(() => {
    fnRef.current = fn;
  });
  useEffect(() => {
    optsRef.current = { toastOnError, toastPrefix };
  });

  const run = useCallback(async (signal: AbortSignal) => {
    setLoading(true);
    setError(undefined);
    try {
      const result = await fnRef.current(signal);
      if (!signal.aborted) {
        setData(result);
      }
    } catch (err) {
      if (signal.aborted) return;
      const apiError =
        err instanceof ApiError
          ? err
          : new ApiError(undefined, extractDetail(err), err);
      // 401 is already handled by the interceptor; don't double-toast.
      if (apiError.status !== 401) {
        setError(apiError);
        const { toastOnError: toastOn, toastPrefix: prefix } = optsRef.current;
        if (toastOn) {
          const p = prefix ? `${prefix}: ` : "";
          toast.error(`${p}${apiError.detail}`);
        }
      }
    } finally {
      if (!signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (!enabled) {
      // Disabled mode: not loading, no in-flight request.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(false);
      return;
    }
    const ctrl = new AbortController();
    void run(ctrl.signal);
    return () => ctrl.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, run, ...deps]);

  const refetch = useCallback(async () => {
    const ctrl = new AbortController();
    await run(ctrl.signal);
  }, [run]);

  return { data, error, loading, refetch };
}
