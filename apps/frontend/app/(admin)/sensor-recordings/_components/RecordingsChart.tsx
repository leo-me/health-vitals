"use client";

import { useMemo } from "react";
import { format, parseISO } from "date-fns";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
} from "recharts";
import type { SensorRecordingResponse } from "@/types/backend";

interface RecordingsChartProps {
  data: SensorRecordingResponse[];
}

/** Extract a single scalar value from a recording's `data` payload, if possible. */
function scalarValue(payload: Record<string, unknown>): number | null {
  // Common shapes the backend stores under `data`:
  //   {value: 72}          — heart rate, eda, bvp, ibi, temp
  //   {x: ..., y: ..., z}  — accelerometer raw axes (we plot magnitude)
  if (typeof payload.value === "number") return payload.value;
  if (
    typeof payload.x === "number" &&
    typeof payload.y === "number" &&
    typeof payload.z === "number"
  ) {
    return Math.sqrt(payload.x ** 2 + payload.y ** 2 + payload.z ** 2);
  }
  return null;
}

export function RecordingsChart({ data }: RecordingsChartProps) {
  const series = useMemo(() => {
    return data
      .map((r) => ({ time: r.timestamp, value: scalarValue(r.data) }))
      .filter((p): p is { time: string; value: number } => p.value !== null)
      .sort((a, b) => a.time.localeCompare(b.time));
  }, [data]);

  if (series.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-muted-foreground text-sm">
        No numeric values to plot for this sensor type.
      </div>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={series}>
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
            dataKey="value"
            stroke="#00D4AA"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
