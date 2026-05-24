"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { toast } from "sonner";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

interface UUIDCellProps {
  value: string;
  length?: number;
  className?: string;
}

export function UUIDCell({ value, length = 8, className }: UUIDCellProps) {
  const [copied, setCopied] = useState(false);

  const display =
    value.length <= length ? value : `${value.slice(0, length)}…${value.slice(-4)}`;

  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      toast.success("Copied to clipboard");
      setTimeout(() => setCopied(false), 1500);
    } catch {
      toast.error("Couldn't copy — clipboard unavailable");
    }
  }

  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <button
            type="button"
            onClick={copy}
            className={cn(
              "inline-flex items-center gap-1.5 font-mono text-xs text-foreground/80 hover:text-foreground transition-colors",
              className,
            )}
          >
            <span>{display}</span>
            {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3 opacity-50" />}
          </button>
        }
      />
      <TooltipContent side="top" className="font-mono text-[10px]">
        {value}
      </TooltipContent>
    </Tooltip>
  );
}
