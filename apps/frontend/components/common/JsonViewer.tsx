"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface JsonViewerProps {
  data: unknown;
  className?: string;
}

export function JsonViewer({ data, className }: JsonViewerProps) {
  const [copied, setCopied] = useState(false);
  const text = JSON.stringify(data, null, 2);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast.success("JSON copied");
      setTimeout(() => setCopied(false), 1500);
    } catch {
      toast.error("Couldn't copy");
    }
  }

  return (
    <div className={cn("relative bg-muted/40 border rounded-lg", className)}>
      <Button
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2 h-7 px-2"
        onClick={copy}
      >
        {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
      </Button>
      <pre className="p-4 pr-12 text-xs font-mono whitespace-pre-wrap break-all overflow-auto max-h-[60vh]">
        {text}
      </pre>
    </div>
  );
}
