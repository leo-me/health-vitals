"use client";

import { useCdlHealth } from "@/hooks/useCdlHealth";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export function CdlHealthBadge() {
  const { status, lastChecked } = useCdlHealth();

  const dotColor =
    status === "online"
      ? "bg-vital"
      : status === "offline"
      ? "bg-danger"
      : "bg-muted-foreground";

  const label =
    status === "online" ? "CDL online" : status === "offline" ? "CDL offline" : "CDL …";

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground cursor-default">
            <span
              className={cn(
                "inline-block w-2 h-2 rounded-full",
                dotColor,
                status === "unknown" && "animate-pulse",
              )}
            />
            <span>{label}</span>
          </div>
        }
      />
      <TooltipContent side="bottom">
        {lastChecked
          ? `Last check: ${lastChecked.toLocaleTimeString()}`
          : "Polling…"}
      </TooltipContent>
    </Tooltip>
  );
}
