"use client";

import { useCallback } from "react";
import { useApi } from "./useApi";
import { getInference } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/authStore";
import type { InferenceResponse } from "@/types/cdl";

export function useInference() {
  const userId = useAuthStore((s) => s.userId);
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      userId
        ? getInference(userId, signal)
        : Promise.resolve<InferenceResponse | undefined>(undefined),
    [userId],
  );
  // Inference can return 503 when no model is registered — don't toast that.
  return useApi(fetcher, {
    enabled: !!userId,
    deps: [userId],
    toastOnError: false,
  });
}
