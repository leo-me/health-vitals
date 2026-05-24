"use client";

import { useCallback } from "react";
import { useApi } from "./useApi";
import { getAdapterData } from "@/lib/api/endpoints";
import { useAuthStore } from "@/store/authStore";
import type { AdapterResponse, ConsumerType } from "@/types/cdl";

export function useAdapter(consumerType: ConsumerType) {
  const userId = useAuthStore((s) => s.userId);
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      userId
        ? getAdapterData(consumerType, userId, signal)
        : Promise.resolve<AdapterResponse | undefined>(undefined),
    [consumerType, userId],
  );
  return useApi(fetcher, {
    enabled: !!userId,
    deps: [consumerType, userId],
    toastPrefix: `Adapter ${consumerType}`,
  });
}
