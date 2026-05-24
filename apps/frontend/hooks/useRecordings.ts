"use client";

import { useCallback } from "react";
import { useApi } from "./useApi";
import { listSensorRecordings } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/authStore";
import type { SensorRecordingsQuery } from "@/types/backend";

export function useRecordings(query: SensorRecordingsQuery, enabled: boolean = true) {
  const userId = useAuthStore((s) => s.userId);
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      userId ? listSensorRecordings(userId, query, signal) : Promise.resolve([]),
    [userId, query],
  );
  return useApi(fetcher, {
    enabled: enabled && !!userId,
    deps: [
      userId,
      query.sensor_type ?? "",
      query.start ?? "",
      query.end ?? "",
      query.page ?? 1,
      query.page_size ?? 10,
    ],
    toastPrefix: "Recordings",
  });
}
