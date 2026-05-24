"use client";

import { useMemo, useState } from "react";
import { format, subDays, isValid } from "date-fns";
import { CalendarIcon, ChevronLeft, ChevronRight } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { UUIDCell } from "@/components/common/UUIDCell";
import { TimestampCell } from "@/components/common/TimestampCell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { SENSOR_TYPES, type SensorType } from "@/types/backend";
import { useRecordings } from "@/hooks/useRecordings";
import { RecordingsChart } from "./_components/RecordingsChart";

type SensorFilter = SensorType | "all";

function toMidnightISO(d: Date | undefined): string | undefined {
  return d && isValid(d) ? d.toISOString() : undefined;
}

function DatePickerField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: Date | undefined;
  onChange: (d: Date | undefined) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="space-y-1.5 min-w-44">
      <Label className="text-xs text-muted-foreground">{label}</Label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger
          render={
            <Button variant="outline" className="w-full justify-start font-normal">
              <CalendarIcon className="w-4 h-4 mr-2" />
              {value ? format(value, "MMM d, yyyy") : "Pick a date"}
            </Button>
          }
        />
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={value}
            onSelect={(d) => {
              onChange(d);
              setOpen(false);
            }}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}

export default function SensorRecordingsPage() {
  const [sensorType, setSensorType] = useState<SensorFilter>("heart_rate");
  const [start, setStart] = useState<Date | undefined>(() => subDays(new Date(), 1));
  const [end, setEnd] = useState<Date | undefined>(() => new Date());
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  const query = useMemo(
    () => ({
      sensor_type: sensorType === "all" ? undefined : sensorType,
      start: toMidnightISO(start),
      end: toMidnightISO(end),
      page,
      page_size: pageSize,
    }),
    [sensorType, start, end, page, pageSize],
  );

  const recordings = useRecordings(query);

  const rows = recordings.data ?? [];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <PageHeader
        title="Sensor recordings"
        description="Query the raw sensor recordings stored by the backend."
      />

      <div className="bg-card border rounded-lg shadow-sm p-4 mb-6 flex flex-wrap items-end gap-3">
        <div className="space-y-1.5 min-w-40">
          <Label className="text-xs text-muted-foreground">Sensor type</Label>
          <Select
            value={sensorType}
            onValueChange={(v) => {
              setSensorType(v as SensorFilter);
              setPage(1);
            }}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All types</SelectItem>
              {SENSOR_TYPES.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <DatePickerField label="Start" value={start} onChange={setStart} />
        <DatePickerField label="End" value={end} onChange={setEnd} />

        <div className="space-y-1.5 w-28">
          <Label htmlFor="page-size" className="text-xs text-muted-foreground">
            Page size
          </Label>
          <Input
            id="page-size"
            type="number"
            min={1}
            max={1000}
            value={pageSize}
            onChange={(e) => {
              setPageSize(Math.max(1, Number(e.target.value) || 50));
              setPage(1);
            }}
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1 || recordings.loading}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Badge variant="secondary" className="font-mono">
            page {page}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={rows.length < pageSize || recordings.loading}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="bg-card border rounded-lg shadow-sm p-6 mb-6">
        <h2 className="font-heading text-lg font-bold mb-3">Chart</h2>
        {recordings.loading && recordings.data === undefined ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <RecordingsChart data={rows} />
        )}
      </div>

      <div className="bg-card border rounded-lg shadow-sm overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Device</TableHead>
              <TableHead>Sensor</TableHead>
              <TableHead>Data</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {recordings.loading && recordings.data === undefined ? (
              [0, 1, 2, 3].map((i) => (
                <TableRow key={i}>
                  <TableCell colSpan={4}>
                    <Skeleton className="h-8 w-full" />
                  </TableCell>
                </TableRow>
              ))
            ) : rows.length > 0 ? (
              rows.map((r) => (
                <TableRow key={r.id} className="hover:bg-muted/40">
                  <TableCell>
                    <TimestampCell value={r.timestamp} />
                  </TableCell>
                  <TableCell>
                    <UUIDCell value={r.device_id} />
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="capitalize font-mono text-[10px]">
                      {r.sensor_type}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <code className="font-mono text-[11px] text-muted-foreground">
                      {JSON.stringify(r.data)}
                    </code>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground py-12">
                  No recordings match these filters.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
