"use client";

import { cn } from "@/lib/utils";

/**
 * Server-friendly placeholder that AuthGate renders before auth state resolves.
 * Must produce identical output on the server and the first client render so
 * we don't trigger a hydration mismatch when localStorage is checked later.
 */
export function PageSkeleton({ className }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={cn(
        "min-h-screen bg-[color:var(--app-bg)] grid grid-cols-[16rem_1fr]",
        className,
      )}
    >
      {/* Sidebar placeholder */}
      <div className="bg-sidebar h-screen" />
      {/* Main area placeholder */}
      <div className="p-8 space-y-6">
        <div className="h-8 w-48 bg-muted rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-28 bg-card border rounded-lg shadow-sm animate-pulse" />
          ))}
        </div>
        <div className="h-80 bg-card border rounded-lg shadow-sm animate-pulse" />
      </div>
    </div>
  );
}
