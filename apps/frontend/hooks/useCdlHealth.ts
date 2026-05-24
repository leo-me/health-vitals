"use client";

import { useEffect, useRef, useState } from "react";
import { pingCdl } from "@/lib/api/endpoints";

export type CdlHealth = "unknown" | "online" | "offline";

/**
 * Polls CDL `/ping` every `intervalMs` (default 30s). Doesn't toast on
 * failure — the badge itself is the signal. Aborts the in-flight request
 * when the component unmounts.
 */
export function useCdlHealth(intervalMs: number = 30_000): {
  status: CdlHealth;
  lastChecked: Date | undefined;
} {
  const [status, setStatus] = useState<CdlHealth>("unknown");
  const [lastChecked, setLastChecked] = useState<Date | undefined>(undefined);
  const ctrlRef = useRef<AbortController | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function check() {
      ctrlRef.current?.abort();
      const ctrl = new AbortController();
      ctrlRef.current = ctrl;
      try {
        await pingCdl(ctrl.signal);
        if (!cancelled) {
          setStatus("online");
          setLastChecked(new Date());
        }
      } catch {
        if (!cancelled && !ctrl.signal.aborted) {
          setStatus("offline");
          setLastChecked(new Date());
        }
      }
    }

    void check();
    const id = setInterval(check, intervalMs);
    return () => {
      cancelled = true;
      clearInterval(id);
      ctrlRef.current?.abort();
    };
  }, [intervalMs]);

  return { status, lastChecked };
}
