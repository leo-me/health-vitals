"use client";

import { useMemo, useState } from "react";
import { Bell } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { UUIDCell } from "@/components/common/UUIDCell";
import { TimestampCell } from "@/components/common/TimestampCell";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAlerts } from "@/hooks/useAlerts";

export default function AlertsPage() {
  const alerts = useAlerts();
  const [filter, setFilter] = useState("");

  const rows = useMemo(() => {
    const all = alerts.data ?? [];
    const sorted = [...all].sort((a, b) => b.created_at.localeCompare(a.created_at));
    const needle = filter.trim().toLowerCase();
    if (!needle) return sorted;
    return sorted.filter((a) => a.content.toLowerCase().includes(needle));
  }, [alerts.data, filter]);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <PageHeader
        title="Alerts"
        description="Alerts generated when sensor recordings breach configured thresholds."
      />

      <div className="bg-card border rounded-lg shadow-sm p-4 mb-6 flex items-end gap-3">
        <div className="space-y-1.5 max-w-md flex-1">
          <Label htmlFor="alert-filter" className="text-xs text-muted-foreground">
            Filter by content
          </Label>
          <Input
            id="alert-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="e.g. heart rate"
          />
        </div>
        <div className="text-xs text-muted-foreground">
          {alerts.data?.length ?? 0} total · {rows.length} shown
        </div>
      </div>

      <div className="bg-card border rounded-lg shadow-sm overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-44">Alert ID</TableHead>
              <TableHead className="w-44">Created</TableHead>
              <TableHead>Content</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {alerts.loading && alerts.data === undefined ? (
              [0, 1, 2].map((i) => (
                <TableRow key={i}>
                  <TableCell colSpan={3}>
                    <Skeleton className="h-8 w-full" />
                  </TableCell>
                </TableRow>
              ))
            ) : rows.length > 0 ? (
              rows.map((a) => (
                <TableRow key={a.id} className="hover:bg-muted/40">
                  <TableCell>
                    <UUIDCell value={a.id} />
                  </TableCell>
                  <TableCell>
                    <TimestampCell value={a.created_at} />
                  </TableCell>
                  <TableCell className="text-sm">{a.content}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} className="text-center text-muted-foreground py-12">
                  <Bell className="w-6 h-6 mx-auto mb-2 opacity-40" />
                  No alerts match.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <p className="mt-4 text-[11px] text-muted-foreground">
        The backend&apos;s <code className="font-mono">AlertResponse</code> currently exposes only{" "}
        <code className="font-mono">id</code>, <code className="font-mono">content</code>, and{" "}
        <code className="font-mono">created_at</code>. Severity, threshold, and resolved-state
        columns will appear here once the backend schema is extended.
      </p>
    </div>
  );
}
