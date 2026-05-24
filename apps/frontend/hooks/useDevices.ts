"use client";

import { useCallback } from "react";
import { useApi } from "./useApi";
import { listDevices } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/authStore";

export function useDevices() {
  const userId = useAuthStore((s) => s.userId);
  const fetcher = useCallback(
    (signal: AbortSignal) => (userId ? listDevices(userId, signal) : Promise.resolve([])),
    [userId],
  );
  return useApi(fetcher, {
    enabled: !!userId,
    deps: [userId],
    toastPrefix: "Devices",
  });
}
