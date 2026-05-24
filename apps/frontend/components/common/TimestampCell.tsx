"use client";

import { format, parseISO, isValid } from "date-fns";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface TimestampCellProps {
  value: string | Date | undefined | null;
  /** date-fns format. Default: "MMM d, HH:mm:ss". */
  pattern?: string;
}

export function TimestampCell({ value, pattern = "MMM d, HH:mm:ss" }: TimestampCellProps) {
  if (!value) return <span className="text-muted-foreground">—</span>;

  const date = value instanceof Date ? value : parseISO(value);
  if (!isValid(date)) {
    return <span className="font-mono text-xs">{String(value)}</span>;
  }

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <span className="font-mono text-xs cursor-default">{format(date, pattern)}</span>
        }
      />
      <TooltipContent side="top" className="font-mono text-[10px]">
        {date.toISOString()}
      </TooltipContent>
    </Tooltip>
  );
}
