"use client";

import { useCallback } from "react";
import { useApi } from "./useApi";
import { getOverview } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/authStore";
import type { OverviewResponse } from "@/types/cdl";

export function useOverview(days: number = 7) {
  const userId = useAuthStore((s) => s.userId);
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      userId
        ? getOverview(userId, days, signal)
        : Promise.resolve<OverviewResponse | undefined>(undefined),
    [userId, days],
  );
  return useApi(fetcher, {
    enabled: !!userId,
    deps: [userId, days],
    toastPrefix: "Overview",
  });
}
