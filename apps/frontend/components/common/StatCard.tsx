"use client";

import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

interface StatCardProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number | null | undefined;
  hint?: string;
  loading?: boolean;
  accent?: "vital" | "danger" | "neutral";
}

const ACCENT_MAP: Record<NonNullable<StatCardProps["accent"]>, string> = {
  vital: "bg-vital/10 text-vital",
  danger: "bg-danger/10 text-danger",
  neutral: "bg-muted text-muted-foreground",
};

export function StatCard({
  icon: Icon,
  label,
  value,
  hint,
  loading,
  accent = "neutral",
}: StatCardProps) {
  return (
    <div className="bg-card border rounded-lg shadow-sm p-5 flex items-start gap-4">
      <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center shrink-0", ACCENT_MAP[accent])}>
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">
          {label}
        </div>
        <div className="mt-1 text-2xl font-bold font-heading tabular-nums">
          {loading ? (
            <Skeleton className="h-7 w-20 mt-1" />
          ) : value === null || value === undefined ? (
            <span className="text-muted-foreground">—</span>
          ) : (
            value
          )}
        </div>
        {hint && (
          <div className="text-xs text-muted-foreground mt-1 truncate">{hint}</div>
        )}
      </div>
    </div>
  );
}
