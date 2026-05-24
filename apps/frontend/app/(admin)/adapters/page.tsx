"use client";

import { useState } from "react";
import { RefreshCw } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { JsonViewer } from "@/components/common/JsonViewer";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CONSUMER_TYPES, type ConsumerType } from "@/types/cdl";
import { useAdapter } from "@/hooks/useAdapter";

const CONSUMER_DESCRIPTIONS: Record<ConsumerType, string> = {
  smart_watch:
    "Compact projection with computed stress_level + sweat_level. Cached 5 s.",
  web_dashboard:
    "Like smart_watch but drops EDA so the dashboard only shows derived levels. Cached 1 s.",
  ml: "Pass-through raw signals + EDA components, intended for downstream ML. Cached 60 s.",
  researcher:
    "ACC expanded back to x/y/z axes; all signals retained. Cached 10 min, emitted as CSV upstream.",
};

export default function AdaptersPage() {
  const [consumerType, setConsumerType] = useState<ConsumerType>("smart_watch");
  const adapter = useAdapter(consumerType);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <PageHeader
        title="Adapter preview"
        description="Inspect how the Consumer Delivery Layer projects sensor data per consumer."
      />

      <div className="bg-card border rounded-lg shadow-sm p-4 mb-6 flex flex-wrap items-end gap-4">
        <div className="space-y-1.5 min-w-64">
          <Label className="text-xs text-muted-foreground">Consumer type</Label>
          <Select value={consumerType} onValueChange={(v) => setConsumerType(v as ConsumerType)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {CONSUMER_TYPES.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <p className="text-xs text-muted-foreground flex-1 min-w-0">
          {CONSUMER_DESCRIPTIONS[consumerType]}
        </p>
        <Button variant="outline" size="sm" onClick={() => adapter.refetch()} disabled={adapter.loading}>
          <RefreshCw className={adapter.loading ? "w-4 h-4 mr-1 animate-spin" : "w-4 h-4 mr-1"} />
          Refresh
        </Button>
      </div>

      <div className="mb-2 flex items-center gap-2">
        <Badge variant="secondary" className="font-mono text-[10px]">
          GET /api/v1/data/{consumerType}/{`{user_id}`}
        </Badge>
      </div>

      {adapter.loading && adapter.data === undefined ? (
        <Skeleton className="h-64 w-full" />
      ) : adapter.error ? (
        <div className="bg-card border rounded-lg shadow-sm p-6 text-sm text-muted-foreground">
          {adapter.error.detail}
        </div>
      ) : adapter.data ? (
        <JsonViewer data={adapter.data} />
      ) : (
        <div className="bg-card border rounded-lg shadow-sm p-6 text-sm text-muted-foreground">
          No data.
        </div>
      )}
    </div>
  );
}
