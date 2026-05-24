"use client";

import { useCallback } from "react";
import { useApi } from "./useApi";
import { listAlerts } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/authStore";

export function useAlerts() {
  const userId = useAuthStore((s) => s.userId);
  const fetcher = useCallback(
    (signal: AbortSignal) => (userId ? listAlerts(userId, signal) : Promise.resolve([])),
    [userId],
  );
  return useApi(fetcher, {
    enabled: !!userId,
    deps: [userId],
    toastPrefix: "Alerts",
  });
}
