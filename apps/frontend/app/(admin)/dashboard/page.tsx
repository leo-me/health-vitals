"use client";

import { useMemo } from "react";
import {
  Cpu,
  Activity,
  Bell,
  HeartPulse,
  AlertCircle,
} from "lucide-react";
import { format, parseISO, subHours } from "date-fns";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
} from "recharts";
import { PageHeader } from "@/components/layout/PageHeader";
import { StatCard } from "@/components/common/StatCard";
import { useDevices } from "@/hooks/useDevices";
import { useAlerts } from "@/hooks/useAlerts";
import { useOverview } from "@/hooks/useOverview";
import { useInference } from "@/hooks/useInference";
import { useRecordings } from "@/hooks/useRecordings";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

function last24h(): { start: string; end: string } {
  const end = new Date();
  const start = subHours(end, 24);
  return { start: start.toISOString(), end: end.toISOString() };
}

export default function DashboardPage() {
  const devices = useDevices();
  const alerts = useAlerts();
  const overview = useOverview(7);
  const inference = useInference();
  const recentQuery = useMemo(() => ({ ...last24h(), page_size: 1000 }), []);
  const recent = useRecordings(recentQuery);

  // Filter overview buckets for heart_rate and sort by time.
  const heartRateSeries = useMemo(() => {
    if (!overview.data) return [];
    return overview.data.buckets
      .filter((b) => b.sensor_type === "heart_rate" && b.avg !== null)
      .map((b) => ({
        time: b.bucket,
        avg: b.avg as number,
        min: b.min,
        max: b.max,
      }))
      .sort((a, b) => a.time.localeCompare(b.time));
  }, [overview.data]);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <PageHeader
        title="Dashboard"
        description="Live overview of your connected devices, recent vitals, and alerts."
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          icon={Cpu}
          label="Devices"
          value={devices.data?.length}
          loading={devices.loading && devices.data === undefined}
          accent="neutral"
        />
        <StatCard
          icon={Activity}
          label="Recordings (24h)"
          value={recent.data?.length}
          loading={recent.loading && recent.data === undefined}
          accent="vital"
        />
        <StatCard
          icon={Bell}
          label="Alerts"
          value={alerts.data?.length}
          loading={alerts.loading && alerts.data === undefined}
          accent={alerts.data && alerts.data.length > 0 ? "danger" : "neutral"}
        />
        <StatCard
          icon={HeartPulse}
          label="Stress prediction"
          value={
            inference.data ? inference.data.label.replace("_", " ") : undefined
          }
          hint={
            inference.data
              ? `model ${inference.data.model.model_name}`
              : inference.error
              ? "model unavailable"
              : undefined
          }
          loading={inference.loading && inference.data === undefined}
          accent={inference.data?.label === "stress" ? "danger" : "vital"}
        />
      </div>

      <div className="bg-card border rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-baseline justify-between mb-4">
          <div>
            <h2 className="font-heading text-lg font-bold">7-day heart rate</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Hourly bucketed average from the Consumer Delivery Layer.
            </p>
          </div>
          {overview.data && (
            <Badge variant="secondary" className="font-mono text-[10px]">
              {overview.data.cache_hit ? "cache hit" : `db ${overview.data.db_ms?.toFixed?.(1) ?? "?"} ms`}
            </Badge>
          )}
        </div>
        {overview.loading && overview.data === undefined ? (
          <Skeleton className="h-72 w-full" />
        ) : overview.error ? (
          <div className="h-72 flex flex-col items-center justify-center text-muted-foreground">
            <AlertCircle className="w-6 h-6 mb-2" />
            <span className="text-sm">{overview.error.detail}</span>
          </div>
        ) : heartRateSeries.length === 0 ? (
          <div className="h-72 flex items-center justify-center text-muted-foreground text-sm">
            No heart-rate buckets in the last 7 days.
          </div>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={heartRateSeries}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis
                  dataKey="time"
                  tickFormatter={(v) => format(parseISO(v), "MMM d HH:mm")}
                  fontSize={11}
                  stroke="#64748B"
                />
                <YAxis fontSize={11} stroke="#64748B" />
                <ChartTooltip
                  labelFormatter={(v) => format(parseISO(String(v)), "PPpp")}
                  contentStyle={{ borderRadius: 8, fontSize: 12 }}
                />
                <Line
                  type="monotone"
                  dataKey="avg"
                  stroke="#00D4AA"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
